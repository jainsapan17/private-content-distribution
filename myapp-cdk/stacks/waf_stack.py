from aws_cdk import Stack
from aws_cdk import aws_wafv2 as wafv2
from constructs import Construct

class WAFStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create WAF WebACL
        self.web_acl = wafv2.CfnWebACL(
            self, "GeoRestrictWebACL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            scope="CLOUDFRONT",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="GeoRestrictWebACL",
                sampled_requests_enabled=True
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="GeoRestrictionRule",
                    priority=1,
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        not_statement=wafv2.CfnWebACL.NotStatementProperty(
                            statement=wafv2.CfnWebACL.StatementProperty(
                                geo_match_statement=wafv2.CfnWebACL.GeoMatchStatementProperty(
                                    country_codes=["US", "FR", "GB"]
                                )
                            )
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="GeoRestrictionRule",
                        sampled_requests_enabled=True
                    )
                )
            ]
        )
