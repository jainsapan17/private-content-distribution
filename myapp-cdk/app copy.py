#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from myapp_cdk.cloudfront_stack import CloudFrontStack

app = App()

CloudFrontStack(app, "CloudFrontStack",
    env=Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    application_name="cms",
    environment="dev",
    enable_real_time_logs="Yes",
    kinesis_stream_arn="arn:aws:kinesis:region:account-id:stream/stream-name",
)

app.synth()