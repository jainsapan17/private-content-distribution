################################################################################################# 
# Author        : Sapan Jain
# Status        : Working
# Version       : V2.1
# Iteration     : Create S3 origin bucket
# Purpose       : Creates CloudFront Distribution and its componenets to serve private content
#
# Pre-req       : NA
#################################################################################################
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy
)
import random
import string
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Generate a random string of 8 lowercase characters
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))

        self.bucket = s3.Bucket(self, "PrivateContentBucket",
            bucket_name=f"{application_name}-{environment}-bucket-{random_suffix}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,  # Be cautious with this in production
            auto_delete_objects=True  # Be cautious with this in production
        )