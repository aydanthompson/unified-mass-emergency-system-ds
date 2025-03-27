from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_apigateway as api_gw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from constructs import Construct


class MyBucketStack(Stack):
    def __init__(self, scope: Construct, id: str, lab_role_arn: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        s3.Bucket(
            self,
            "TestBucket01",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
