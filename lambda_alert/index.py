import json
import os

import boto3

TOPIC_ARN = os.getenv("TOPIC_ARN")
SENSOR_THRESHOLD = float(os.getenv("SENSOR_THRESHOLD", "30.0"))
sns_client = boto3.client("sns")


def handler(event, context):
    try:
        message = {
            "alert": "Test Alert",
            "details": "Triggered from event: " + str(event),
        }

        response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(message),
            Subject="Test Alert from alert_lambda",
        )
        print("SNS publish response:", response)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Alert published successfully!"}),
        }
    except Exception as ex:
        print("Error in alert_lambda:", ex)

        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(ex)}),
        }
