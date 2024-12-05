################################################################################################# 
# Author        : Sapan Jain
# Status        : Working
# Version       : V2.4
# Iteration     : Adding WAF and OAC to all origins
# Purpose       : Creates CloudFront Distribution and its componenets to serve private content
#
# Pre-req       : Signer stack and origin stack
#################################################################################################

from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront, 
    aws_s3 as s3, 
    aws_iam as iam,
    # aws_wafv2 as wafv2,
    RemovalPolicy
)
# from aws_cdk.aws_cloudfront_origins import S3Origin
import random
import string
from aws_cdk.aws_cloudfront_origins import S3BucketOrigin
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct

class CloudFrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, membership_levels: list, signer_public_keys: dict, web_acl_id: str, **kwargs) -> None:
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
        self.bucket_name = self.bucket.bucket_name

        # Deploy sample content to the bucket
        for level in membership_levels:
            BucketDeployment(self, f"Deploy{level.capitalize()}Content",
                sources=[Source.asset(f"./sample_content/{level}")],
                destination_bucket=self.bucket,
                destination_key_prefix=level,
                retain_on_delete=False,
            )

        # Create Origin Access Control
        oac = cloudfront.CfnOriginAccessControl(self, "OAC",
            origin_access_control_config={
                "name": f"{application_name}-{environment} OAC for S3",
                "originAccessControlOriginType": "s3",
                "signingBehavior": "always",
                "signingProtocol": "sigv4"
            }
        )

        # Create key groups for each subscription level
        key_groups = {
            level: cloudfront.KeyGroup(self, f"{level.capitalize()}KeyGroup",
                items=[signer_public_keys[level]],
                comment=f"Key group for {level} subscription"
            ) for level in membership_levels
        }

        # Create origins for each subscription level
        origins = {
            level: S3BucketOrigin(
                self.bucket,
                origin_path=f"/{level}"
            ) for level in membership_levels
        }

        # Create distribution with default behavior
        distribution = cloudfront.Distribution(self, "PrivateDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=S3BucketOrigin(self.bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                f"/{level}/*": cloudfront.BehaviorOptions(
                    origin=origins[level],
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    trusted_key_groups=[key_groups[l] for l in membership_levels if membership_levels.index(l) >= membership_levels.index(level)]
                ) for level in membership_levels
            },
            web_acl_id=web_acl_id
        )
        self.distribution_domain_name = distribution.distribution_domain_name

        # Add OAC to all origins in the distribution
        cfn_distribution = distribution.node.default_child
        for i, level in enumerate(membership_levels):
            cfn_distribution.add_override(f"Properties.DistributionConfig.Origins.{i}.S3OriginConfig.OriginAccessIdentity", "")
            cfn_distribution.add_override(f"Properties.DistributionConfig.Origins.{i}.OriginAccessControlId", oac.get_att("Id"))

        # Update bucket policy to allow access from CloudFront OAC
        self.bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[self.bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
            conditions={
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                }
            }
        ))