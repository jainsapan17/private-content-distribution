# private-content-distribution
This project contains the AWS CDK infrastructure code for StreamLearn's tiered content distribution system. It sets up a secure, scalable content delivery network using Amazon S3, CloudFront, and WAF.

## Project Structure

- `app.py`: The main CDK app file that defines and creates the stacks.
- `stacks/`:
  - `signer_stack.py`: Creates CloudFront public keys for each subscription tier.
  - `waf_stack.py`: Sets up AWS WAF with geo-restriction rules.
  - `cloudfront_stack.py`: Configures S3 bucket, CloudFront distribution, and associated behaviors.

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.7 or later
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Required Python packages (install using `pip install -r requirements.txt`)
- RSA key-pairs (need to provide Public Key content as input, for each membership level)

## Project Structure

```
.
├── stacks/
│   ├── cloudfront_stack.py
│   ├── signer_stack.py
│   └── waf_stack.py
├── sample_content/
│   ├── basic/
│   │   └── basic_content.py
│   ├── standard/
│   │   └── standard_content.py
│   └── premium/
│       └── premium_content.py
├── app.py
├── requirements.txt
└── README.md
```

## Configuration

Before deploying, ensure you've set the following in `app.py`:

- `APPLICATON_NAME`: The name of your application (default: 'StreamLearn')
- `ENVIRONMENT`: The deployment environment (e.g., 'dev', 'prod')
- `MEMBERSHIP_LEVELS`: A dictionary containing the subscription levels and their corresponding encoded public keys.

## Deployment

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. Synthesize the CloudFormation template:
    ```
    cdk synth
    ```

3. Deploy the stacks:
    ```
    cdk deploy --all
    ```

## Stacks

### SignerStack

Creates CloudFront public keys for each subscription tier, which are used for signing cookies.

### WAFStack

Sets up an AWS WAF WebACL with geo-restriction rules. By default, it allows traffic from the US, France, and the UK.

### CloudFrontStack

- Creates an S3 bucket for content storage
- Sets up a CloudFront distribution with behaviors for each subscription tier
- Configures Origin Access Control (OAC) for secure S3 access
- Creates key groups for each subscription level
- Deploys sample content to the S3 bucket

## Outputs

After deployment, the following outputs will be displayed:

- `BucketName`: The name of the created S3 bucket
- `DistributionDomainName`: The domain name of the CloudFront distribution

## Security Considerations

- The S3 bucket is configured with `RemovalPolicy.DESTROY` and `auto_delete_objects=True`. Be cautious with these settings in a production environment.
- Ensure that the encoded public keys in `MEMBERSHIP_LEVELS` are kept secure and not exposed publicly. As a best practice, store them in AWS secrets Manager.
- Review and adjust the WAF rules as needed for your specific use case.

## Customization

- To add or modify subscription tiers, update the `MEMBERSHIP_LEVELS` dictionary in `app.py` (and also make required updates within CloudFrontStack).
- To change the allowed countries in the WAF, modify the `country_codes` list in the `WAFStack`.
- Adjust the CloudFront behaviors in `CloudFrontStack` if you need to change caching or viewer policies.
- Additionally, add custom origin and/or other origins if required to serve other dynamic private/public content.

## Cleanup

To remove all resources created by this project:
    ```
    cdk destroy --all
    ```

Note: This will delete all resources, including the S3 bucket and its contents. Ensure you have backups of any important data before proceeding.

## Status
Working

## Author
Sapan Jain

## Version
2.0

## Date
2024-12-03

## License

Copyright (c) 2024 Sapan Jain

All rights reserved.

This software and associated documentation files (the "Software") are the proprietary property of Sapan Jain. The Software is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties.

Unauthorized copying, modification, distribution, or use of this Software, via any medium, is strictly prohibited without the express written permission of the copyright holder.

The Software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the author or copyright holder be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.

Any use of this Software is at your own risk. The author is not responsible for any damages, losses, or consequences that may arise from the use, misuse, or malfunction of the Software. By using this Software, you acknowledge and agree that you assume all risks associated with its use and that the author shall not be held liable for any direct, indirect, incidental, special, exemplary, or consequential damages resulting from the use or inability to use the Software.

For permission requests, please contact: Sapan Jain at jainsapan171@gmail.com
