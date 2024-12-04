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
from aws_cdk import App

from stacks.origin_stack import S3Stack
from stacks.cloudfront_stack import CloudFrontStack
from stacks.signer_stack import SignerStack
# --------------------------- #
APPLICATON_NAME = 'myapp'
ENVIRONMENT = 'dev'
# --------------------------- #
app = App()
# --------------------------- #
s3_stack = S3Stack(app, "S3OriginStack", application_name=APPLICATON_NAME, environment=ENVIRONMENT)
signer_stack = SignerStack(app, "SignerStack", 
                           application_name=APPLICATON_NAME, 
                           environment=ENVIRONMENT,
                           encoded_key='''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArXj8ZDw5cga8421IqrfX
7Bf45PZJTEzWfdGCF3suSSuF5ZqVjM6y6rE6Qv0WlHagDq0wJwN2BUhQ11GwkJzx
aRkjda+w9CGKh+9AQp6KK54KdZW6FGaQBF4RVOGp0oYfYNj7rZKQZDkqcgtqSDra
THp7U0EcDiXVnFxQOUO3u3h4EoQdtBYMEVo6zI1ve84PAGda0+mUfv0wdNvzIKSn
lgmEBbCv5UD64J5lgpvHIWPvWqiVSe4yZz5wvrwuq7Bc3aV1X7iDuwxbb5trr+xC
dV71iLrnKPoh0mXaEXY1g5sRrITr8JPYLi0I5zeUwh9eGtmmxAOkFNG+QmZBaRK6
twIDAQAB
-----END PUBLIC KEY-----'''
                           )
cloudfront_stack = CloudFrontStack(app, "CloudFrontStack",
                                   application_name=APPLICATON_NAME, 
                                   environment=ENVIRONMENT,
                                   bucket=s3_stack.bucket,
                                   signer_public_key=signer_stack.public_key
                                   )
# --------------------------- #
app.synth()
# --------------------------- #