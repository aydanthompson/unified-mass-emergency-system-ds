import aws_cdk as cdk
from aws_cdk import CliCredentialsStackSynthesizer

from aws.aws_stack import MyBucketStack

app = cdk.App()

account_id = app.node.try_get_context("account_id")
lab_role_arn = app.node.try_get_context("lab_role_arn")

MyBucketStack(
    app,
    "MyBucketStack",
    synthesizer=CliCredentialsStackSynthesizer(),
    lab_role_arn=lab_role_arn,
)

app.synth()
