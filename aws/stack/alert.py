import os

from aws_cdk import Stack
from aws_cdk import aws_iot as iot
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from constructs import Construct


class IoTAlertStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        lab_role_arn: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # Gather email addresses.
        emails_raw = os.getenv("ALERT_EMAILS", "")
        emails = [e.strip() for e in emails_raw.split(",") if e.strip()]

        # Gather phone numbers.
        phones_raw = os.getenv("ALERT_PHONE_NUMBERS", "")
        phones = [p.strip() for p in phones_raw.split(",") if p.strip()]

        alert_topic = sns.Topic(self, "IoTAlertTopic")

        # Add subscribers.
        for email in emails:
            alert_topic.add_subscription(subs.EmailSubscription(email))
        for phone in phones:
            alert_topic.add_subscription(subs.SmsSubscription(phone))

        iot.CfnTopicRule(
            self,
            "IoTAlertRule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'sensors/depth/alert'",
                rule_disabled=False,
                actions=[
                    iot.CfnTopicRule.ActionProperty(
                        sns=iot.CfnTopicRule.SnsActionProperty(
                            target_arn=alert_topic.topic_arn,
                            message_format="RAW",
                            role_arn=lab_role_arn,
                        )
                    )
                ],
            ),
            rule_name="IoTAlertRule",
        )
