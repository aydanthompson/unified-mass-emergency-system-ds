import os

from aws_cdk import App, Environment, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iot as iot
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from constructs import Construct


class IoTWeatherAlertStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        lab_role_arn: str,
        sensor_threshold: float,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        alert_emails_env = os.getenv("ALERT_EMAILS", "")
        alert_emails = [
            email.strip() for email in alert_emails_env.split(",") if email.strip()
        ]

        existing_lab_role = iam.Role.from_role_arn(
            self,
            "LabRole",
            lab_role_arn,
            # Prevents attaching new inline policies.
            mutable=False,
        )

        alert_topic = sns.Topic(self, "SensorAlertTopic")
        # Resource-based policy.
        alert_topic.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ArnPrincipal(lab_role_arn)],
                actions=["sns:Publish"],
                resources=["*"],
            )
        )
        for email in alert_emails:
            alert_topic.add_subscription(subs.EmailSubscription(email))

        alert_lambda = _lambda.Function(
            self,
            "AlertLambda",
            code=_lambda.Code.from_asset("lambda_alert"),
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            role=existing_lab_role,
            environment={
                "SENSOR_THRESHOLD": str(sensor_threshold),
                "TOPIC_ARN": alert_topic.topic_arn,
            },
        )
