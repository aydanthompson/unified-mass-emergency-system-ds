#!/usr/bin/env python3
import json
import random
import threading
import time

from awsiot import mqtt_connection_builder

ENDPOINT = "a2j8imicgc27m8-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "DepthSensor1"
PATH_TO_CERT = "/home/ec2-user/cert.pem"
PATH_TO_KEY = "/home/ec2-user/private.key"
PATH_TO_ROOT = "/home/ec2-user/AmazonRootCA1.pem"

ALERT_TOPIC = "sensors/depth/alert"
BATCH_TOPIC = "sensors/depth/batch"
DEVICE_ID = "depth-sensor-1"
THRESHOLD = 40.0
OFFLINE_CHANCE = 0.2
OFFLINE_DURATION = (10, 30)
BATCH_INTERVAL = 20
is_offline = False
local_buffer = []


def main():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        endpoint=ENDPOINT,
        ca_filepath=PATH_TO_ROOT,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
    )
    print("Connecting to IoT...")
    mqtt_connection.connect().result()
    print("Connected.")

    last_batch_time = time.time()
    global is_offline

    while True:
        depth = round(random.uniform(0, 30), 2)
        reading = {
            "device_id": DEVICE_ID,
            "timestamp": time.time(),
            "depth": depth,
        }

        if depth > THRESHOLD and not is_offline:
            mqtt_connection.publish(ALERT_TOPIC, json.dumps(reading))
            print("[LOCAL] ALERT =>", reading)
        else:
            local_buffer.append(reading)

        now = time.time()
        if (now - last_batch_time) >= BATCH_INTERVAL and not is_offline:
            if local_buffer:
                batch_payload = {
                    "device_id": DEVICE_ID,
                    "batch": local_buffer,
                }
                mqtt_connection.publish(BATCH_TOPIC, json.dumps(batch_payload))
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
                is_offline = False
                print("[LOCAL] Sensor back online.")

            threading.Thread(target=back_online, daemon=True).start()

        time.sleep(5)


if __name__ == "__main__":
    main()
