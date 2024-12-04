from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_wafv2 as wafv2,
    aws_iam as iam,
    aws_lambda as lambda_,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct
# from origin_stack import OriginStack
# from signer_stack import SignerStack

class CloudFrontStack(Stack):

    # def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, enable_real_time_logs: str, kinesis_stream_arn: str, **kwargs) -> None:
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, enable_real_time_logs: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # # Create Origin Stack
        # origin_stack = OriginStack(self, "OriginStack",
        #     application=application_name,
        #     environment=environment,
        #     origin_bucket_name="origin",
        #     logging_bucket_name="cms-origin-logging"
        # )

        # # Create Signer Stacks
        # bronze_signer = SignerStack(self, "BronzeSigner", subscription_model="Bronze")
        # silver_signer = SignerStack(self, "SilverSigner", subscription_model="Silver")
        # gold_signer = SignerStack(self, "GoldSigner", subscription_model="Gold")

        # Create CloudFront OAC
        oac = cloudfront.IOriginAccessControl(self, "CloudFrontOAC",
            description="Allow viewers to access Origin only via CloudFront",
            origin_access_control_origin_type=cloudfront.OriginAccessControlOriginType.S3,
            signing_behavior=cloudfront.OriginAccessControlSigningBehavior.ALWAYS,
            signing_protocol=cloudfront.OriginAccessControlSigningProtocol.SIGV4
        )

        # Create Cache Policy
        cache_policy = cloudfront.CachePolicy(self, "CmsCachePolicy",
            comment="Cache policy for CMS application Private CDN",
            default_ttl=3600,
            max_ttl=31536000,
            min_ttl=1,
            name="CMS-Cache-Policy",
            enable_accept_encoding_gzip=True,
            cookie_behavior=cloudfront.CacheCookieBehavior.none(),
            header_behavior=cloudfront.CacheHeaderBehavior.none(),
            query_string_behavior=cloudfront.CacheQueryStringBehavior.none(),
        )

        # Create Origin Request Policy
        origin_request_policy = cloudfront.OriginRequestPolicy(self, "CmsOriginPolicy",
            comment="Origin Policy",
            cookie_behavior=cloudfront.OriginRequestCookieBehavior.none(),
            header_behavior=cloudfront.OriginRequestHeaderBehavior.none(),
            query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.none(),
        )

        # Create CloudFront Distribution
        distribution = cloudfront.Distribution(self, "CloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(origin_stack.default_origin_bucket, origin_access_control=oac),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                cache_policy=cache_policy,
                origin_request_policy=origin_request_policy,
                trusted_key_groups=[bronze_signer.key_group]
            ),
            comment=f"CDN to serve private content for {environment} {application_name}",
            enabled=True,
            http_version=cloudfront.HttpVersion.HTTP2,
            price_class=cloudfront.PriceClass.PRICE_CLASS_200,
            enable_logging=True,
            log_bucket=origin_stack.logging_bucket,
            log_file_prefix="cdn-logs",
        )

        # Add cache behaviors
        self.add_cache_behavior(distribution, "/Gold/Silver/Bronze/*.pdf", [bronze_signer.key_group, silver_signer.key_group, gold_signer.key_group], origin_stack.origin_bucket, cache_policy, origin_request_policy)
        self.add_cache_behavior(distribution, "/Gold/Silver/*.pdf", [silver_signer.key_group, gold_signer.key_group], origin_stack.origin_bucket, cache_policy, origin_request_policy)
        self.add_cache_behavior(distribution, "/Gold/*.pdf", [gold_signer.key_group], origin_stack.origin_bucket, cache_policy, origin_request_policy)

        # Create WAF
        waf = wafv2.CfnWebACL(self, "AwsWaf",
            name="ExampleWebACL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            scope="CLOUDFRONT",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="All",
                sampled_requests_enabled=True
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="GeoRestrictExample",
                    priority=0,
                    action=wafv2.CfnWebACL.RuleActionProperty(allow={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        not_statement=wafv2.CfnWebACL.NotStatementProperty(
                            statement=wafv2.CfnWebACL.StatementProperty(
                                geo_match_statement=wafv2.CfnWebACL.GeoMatchStatementProperty(
                                    country_codes=["US"]
                                )
                            )
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="All",
                        sampled_requests_enabled=True
                    )
                )
            ]
        )

        # Associate WAF with CloudFront distribution
        distribution.add_behavior("/*", origins.S3Origin(origin_stack.default_origin_bucket, origin_access_control=oac),
                                  web_acl_id=waf.attr_arn)

        # Outputs
        CfnOutput(self, "DistributionId", value=distribution.distribution_id)
        CfnOutput(self, "DistributionDomainName", value=distribution.domain_name)

    def add_cache_behavior(self, distribution, path_pattern, key_groups, origin_bucket, cache_policy, origin_request_policy):
        distribution.add_behavior(
            path_pattern,
            origins.S3Origin(origin_bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            cache_policy=cache_policy,
            origin_request_policy=origin_request_policy,
            trusted_key_groups=key_groups
        )
