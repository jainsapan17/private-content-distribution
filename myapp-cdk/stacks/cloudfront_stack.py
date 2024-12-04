################################################################################################# 
# Author        : Sapan Jain
# Status        : Working
# Version       : V2.1
# Iteration     : Create Cloudfront Distribution
# Purpose       : Creates CloudFront Distribution and its componenets to serve private content
#
# Pre-req       : Signer stack and origin stack
#################################################################################################

from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront, 
    aws_s3 as s3, 
    aws_iam as iam
)
# from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_cloudfront_origins import S3BucketOrigin
from constructs import Construct

class CloudFrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, bucket: s3.Bucket, signer_public_key: cloudfront.PublicKey, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Origin Access Control
        oac = cloudfront.CfnOriginAccessControl(self, "OAC",
            origin_access_control_config={
                "name": f"{application_name}-{environment} OAC for S3",
                "originAccessControlOriginType": "s3",
                "signingBehavior": "always",
                "signingProtocol": "sigv4"
            }
        )

        # Create CF Key Group
        key_group = cloudfront.KeyGroup(self, "SignerKeyGroup",
            items=[signer_public_key],
            comment=f"{application_name}-{environment} Key group for signed cookies"
        )

        # Create Cloudfront Distribution
        distribution = cloudfront.Distribution(self, "PrivateDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=S3BucketOrigin(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                trusted_key_groups=[key_group],
            ),
            default_root_object="index.html"
        )

        # Add OAC to the distribution
        cfn_distribution = distribution.node.default_child
        cfn_distribution.add_property_override("DistributionConfig.Origins.0.S3OriginConfig.OriginAccessIdentity", "")
        cfn_distribution.add_property_override("DistributionConfig.Origins.0.OriginAccessControlId", oac.get_att("Id"))

        # Update bucket policy to allow access from CloudFront OAC
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
            conditions={
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                }
            }
        ))