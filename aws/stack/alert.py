import os

from aws_cdk import App, CfnOutput, Environment, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iot as iot
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
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

        lab_role = iam.Role.from_role_arn(
            self,
            "LabRole",
            lab_role_arn,
            # Prevents attaching new inline policies.
            mutable=False,
        )

        self.data_bucket = s3.Bucket(
            self,
            "SensorDataBucket",
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.alert_topic = sns.Topic(self, "SensorAlertTopic")
        # Only a resource-based policy works within learner lab restrictions.
        # Lab role has publish already, this might not be required!
        # self.alert_topic.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         principals=[iam.ArnPrincipal(lab_role_arn)],
        #         actions=["sns:Publish"],
        #         resources=["*"],
        #     )
        # )
        # Add emails from environment variable.
        alert_emails = [
            email.strip()
            for email in os.getenv("ALERT_EMAILS", "").split(",")
            if email.strip()
        ]
        for email in alert_emails:
            self.alert_topic.add_subscription(subs.EmailSubscription(email))

        self.alert_lambda = _lambda.Function(
            self,
            "AlertLambda",
            code=_lambda.Code.from_asset("lambda_alert"),
            handler="index.handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            role=lab_role,
            environment={
                "SENSOR_THRESHOLD": str(sensor_threshold),
                "TOPIC_ARN": self.alert_topic.topic_arn,
            },
        )

        CfnOutput(self, "DataBucketName", value=self.data_bucket.bucket_name)
        CfnOutput(self, "AlertTopicARN", value=self.alert_topic.topic_arn)
        CfnOutput(self, "AlertLambdaARN", value=self.alert_lambda.function_arn)
