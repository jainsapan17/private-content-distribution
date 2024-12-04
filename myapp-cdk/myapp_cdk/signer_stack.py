from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_ssm as ssm,
    CfnOutput,
)
from constructs import Construct

class SignerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, subscription_model: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve public key from SSM Parameter Store
        public_key_value = ssm.StringParameter.from_string_parameter_name(
            self, f"{subscription_model}PublicKey",
            string_parameter_name=f"{subscription_model}-Key"
        ).string_value

        # Create Public Key
        public_key = cloudfront.PublicKey(self, "PublicKey",
            encoded_key=public_key_value,
            comment=f"Public-key for {subscription_model} Members",
            name=f"{subscription_model}-Public-Key"
        )

        # Create Key Group
        self.key_group = cloudfront.KeyGroup(self, "KeyGroup",
            items=[public_key],
            comment=f"Trusted-Key Group for {subscription_model} Members",
            name=f"{subscription_model}-Key-Group"
        )

        # Outputs
        CfnOutput(self, "PublicKeyId", value=public_key.public_key_id)
        CfnOutput(self, "KeyGroupId", value=self.key_group.key_group_id)
