import aws_cdk as cdk
from aws_cdk import LegacyStackSynthesizer

from aws.aws_stack import MyBucketStack

app = cdk.App()

MyBucketStack(
    app,
    "MyBucketStack",
    synthesizer=LegacyStackSynthesizer(),
)

app.synth()
