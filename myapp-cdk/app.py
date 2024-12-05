#################################################################################################
"""
# Author        : Sapan Jain
# Status        : Working
# Version       : V2.1
# Iteration     : Create CloudFront Distribution and its componenets to serve private content
# Purpose       : Creates CloudFront Distribution and its componenets to serve private content
#
# Pre-req       : Private and Public Key
                : Install requirements.txt
"""
#################################################################################################
#!/usr/bin/env python3
import os
from aws_cdk import App, CfnOutput # type: ignore

from stacks.cloudfront_stack import CloudFrontStack
from stacks.signer_stack import SignerStack
from stacks.waf_stack import WAFStack
# --------------------------- #
APPLICATON_NAME = 'StreamLearn'
ENVIRONMENT = 'dev'
MEMBERSHIP_LEVELS = {
    'basic': '''YOUR_BASIC_ENCODED_PUBLIC_KEY_HERE''',
    'standard': '''YOUR_STANDARD_ENCODED_PUBLIC_KEY_HERE''',
    'premium': '''YOUR_PREMIUM_ENCODED_PUBLIC_KEY_HERE'''
}
# --------------------------- #
app = App()
# --------------------------- #
signer_stack = SignerStack(app, "SignerStack", 
                           application_name=APPLICATON_NAME, 
                           environment=ENVIRONMENT,
                           encoded_keys=MEMBERSHIP_LEVELS
                           )
# --------------------------- #
waf_stack = WAFStack(app, "WAFStack",
                    application_name=APPLICATON_NAME, 
                    environment=ENVIRONMENT
                    )
# --------------------------- #
content_delivery_stack = CloudFrontStack(app, "CloudFrontStack",
                                   application_name=APPLICATON_NAME, 
                                   environment=ENVIRONMENT,
                                   membership_levels = list(MEMBERSHIP_LEVELS.keys()),
                                   signer_public_keys=signer_stack.public_keys,
                                   web_acl_id=waf_stack.web_acl.attr_arn
                                   )
# --------------------------- #
# Add outputs
CfnOutput(content_delivery_stack, "BucketName", value=content_delivery_stack.bucket_name)
CfnOutput(content_delivery_stack, "DistributionDomainName", value=content_delivery_stack.distribution_domain_name)
app.synth()
# --------------------------- #