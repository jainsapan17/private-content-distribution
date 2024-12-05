################################################################################################# 
# Author        : Sapan Jain
# Status        : Working
# Version       : V2.1
# Iteration     : Create Cloudfront Public Key for trusted group
# Purpose       : Creates CloudFront Distribution and its componenets to serve private content
#
# Pre-req       : Private and Public Key
#################################################################################################

from aws_cdk import Stack, aws_cloudfront as cloudfront
from constructs import Construct

class SignerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, application_name: str, environment: str, encoded_keys: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.public_keys = {}
        for level, encoded_key in encoded_keys.items():
            self.public_keys[level] = cloudfront.PublicKey(self, f"{level.capitalize()}SignerPublicKey",
                encoded_key=encoded_key,
                comment=f"Public key for {level} subscription signed cookies"
            )