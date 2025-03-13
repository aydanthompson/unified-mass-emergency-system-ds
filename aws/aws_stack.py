from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class MyBucketStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        s3.Bucket(self, "TestBucket01", versioned=True)
