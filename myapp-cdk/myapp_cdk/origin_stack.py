from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class OriginStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, application: str, environment: str, origin_bucket_name: str, logging_bucket_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.origin_bucket = s3.Bucket(self, "OriginBucket",
            bucket_name=f"{self.account}-{origin_bucket_name}-{environment}-{application}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN
        )

        self.logging_bucket = s3.Bucket(self, "LoggingBucket",
            bucket_name=f"{self.account}-{logging_bucket_name}-{environment}-{application}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN
        )

        self.origin_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[self.origin_bucket.arn_for_objects("*")],
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")]
            )
        )

        # Lambda function to create subfolders
        create_subfolders_lambda = lambda_.Function(self, "CreateSubfoldersLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": self.origin_bucket.bucket_name
            }
        )

        self.origin_bucket.grant_read_write(create_subfolders_lambda)

        # Outputs
        CfnOutput(self, "OriginBucketName", value=self.origin_bucket.bucket_name)
        CfnOutput(self, "LoggingBucketName", value=self.logging_bucket.bucket_name)

