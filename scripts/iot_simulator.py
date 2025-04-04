#!/usr/bin/env python3
import json
import random
import threading
import time

from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder

# MQTT configuration.
ENDPOINT = "a2j8imicgc27m8-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "DepthSensor1"
PATH_TO_CERT = "/home/ec2-user/cert.pem"
PATH_TO_KEY = "/home/ec2-user/private.key"
PATH_TO_ROOT = "/home/ec2-user/AmazonRootCA1.pem"

# Topic configuration.
DEVICE_ID = "depth-sensor-1"
ALERT_TOPIC = "sensors/depth/alert"
BATCH_TOPIC = "sensors/depth/batch"

# Device configuration.
MIN_DEPTH = 0
MAX_DEPTH = 50
ALERT_THRESHOLD = 40.0
OFFLINE_CHANCE = 0.1
OFFLINE_DURATION = (30, 60)
BATCH_INTERVAL = 30
READING_FREQUENCY = 5

is_offline = False
local_buffer = []


def main():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        ca_filepath=PATH_TO_ROOT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
    )
    print("Connecting to IoT...")
    mqtt_connection.connect().result()
    print("Connected.")

    global is_offline
    last_batch_time = time.time()

    while True:
        depth = round(random.uniform(MIN_DEPTH, MAX_DEPTH), 2)
        reading = {
            "device_id": DEVICE_ID,
            "timestamp": time.time(),
            "depth": depth,
        }

        # Publish alert.
        if depth > ALERT_THRESHOLD and not is_offline:
            mqtt_connection.publish(
                ALERT_TOPIC,
                json.dumps(reading),
                QoS.AT_LEAST_ONCE,
            )
            print("[LOCAL] ALERT =>", reading)

        local_buffer.append(reading)

        now = time.time()
        # Publish batch.
        if (now - last_batch_time) >= BATCH_INTERVAL and not is_offline:
            if local_buffer:
                batch_payload = {
                    "device_id": DEVICE_ID,
                    "batch": local_buffer,
                }
                mqtt_connection.publish(
                    BATCH_TOPIC,
                    json.dumps(batch_payload),
                    QoS.AT_LEAST_ONCE,
                )
                print("[LOCAL] BATCH =>", len(local_buffer), "readings.")
                local_buffer.clear()
            last_batch_time = now

        # Randomly simulate going offline.
        if not is_offline and random.random() < OFFLINE_CHANCE:
            offline_time = random.uniform(*OFFLINE_DURATION)
            is_offline = True
            print(f"[LOCAL] Sensor going offline for {offline_time:.1f}s.")

            def back_online():
                time.sleep(offline_time)
                global is_offline
                is_offline = False
                print("[LOCAL] Sensor back online.")

            threading.Thread(target=back_online, daemon=True).start()

        time.sleep(READING_FREQUENCY)


if __name__ == "__main__":
    main()
