const fs = require('fs');
const crypto = require('crypto');
const express = require('express');

// Configuration for CloudFront
const CLOUDFRONT_DOMAIN = "your-cloudfront-distribution-domain-name";
const POLICY_DURATION_SECONDS = 3600; // 1 hour validity

// Mapping of membership levels to private key files and key pair IDs
const MEMBERSHIP_CONFIG = {
  basic: {
    privateKeyFile: "./keys/basic_private_key.pem",
    keyPairId: "Basic-Key-Pair-ID",
  },
  standard: {
    privateKeyFile: "./keys/standard_private_key.pem",
    keyPairId: "Standard-Key-Pair-ID",
  },
  premium: {
    privateKeyFile: "./keys/premium_private_key.pem",
    keyPairId: "Premium-Key-Pair-ID",
  },
};

// Helper function to read a private key file
function getPrivateKey(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

// Helper function to generate policy JSON
function generatePolicy(domain, resourcePath, durationSeconds, ipAddress = null) {
  const currentTime = Math.floor(Date.now() / 1000); // Current time in Unix epoch
  const policy = {
    Statement: [
      {
        Resource: `https://${domain}${resourcePath}/*`,
        Condition: {
          DateLessThan: {
            "AWS:EpochTime": currentTime + durationSeconds,
          },
        },
      },
    ],
  };

  // Add IP restriction if provided
  if (ipAddress) {
    policy.Statement[0].Condition.IpAddress = {
      "AWS:SourceIp": ipAddress,
    };
  }

  return JSON.stringify(policy);
}

// Helper function to base64 encode and sanitize string
function base64Encode(input) {
  return Buffer.from(input).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// Function to generate signed cookies
function generateSignedCookies(domain, resourcePath, membershipLevel, ipAddress = null) {
  const config = MEMBERSHIP_CONFIG[membershipLevel];
  if (!config) {
    throw new Error(`Invalid membership level: ${membershipLevel}`);
  }

  const privateKey = getPrivateKey(config.privateKeyFile);
  const policy = generatePolicy(domain, resourcePath, POLICY_DURATION_SECONDS, ipAddress);

  // Sign the policy
  const signer = crypto.createSign('RSA-SHA1');
  signer.update(policy);
  const signature = signer.sign(privateKey);

  // Encode the signature and policy
  const encodedPolicy = base64Encode(policy);
  const encodedSignature = base64Encode(signature);

  return {
    "CloudFront-Policy": encodedPolicy,
    "CloudFront-Signature": encodedSignature,
    "CloudFront-Key-Pair-Id": config.keyPairId,
  };
}

// Express application for demonstration
const app = express();
const PORT = 3000;

// API endpoint to get signed cookies
app.get('/generate-cookies', (req, res) => {
  const { membershipLevel, resourcePath, ipAddress } = req.query;

  if (!membershipLevel || !resourcePath) {
    return res.status(400).send('Membership level and resource path are required');
  }

  try {
    const cookies = generateSignedCookies(CLOUDFRONT_DOMAIN, resourcePath, membershipLevel, ipAddress);

    // Send the cookies in the response headers
    res.setHeader('Set-Cookie', [
      `CloudFront-Policy=${cookies['CloudFront-Policy']}; Domain=${CLOUDFRONT_DOMAIN}; Path=${resourcePath}; Secure; HttpOnly`,
      `CloudFront-Signature=${cookies['CloudFront-Signature']}; Domain=${CLOUDFRONT_DOMAIN}; Path=${resourcePath}; Secure; HttpOnly`,
      `CloudFront-Key-Pair-Id=${cookies['CloudFront-Key-Pair-Id']}; Domain=${CLOUDFRONT_DOMAIN}; Path=${resourcePath}; Secure; HttpOnly`,
    ]);

    res.send('Signed cookies generated and sent as Set-Cookie headers.');
  } catch (error) {
    console.error(error);
    res.status(500).send('Error generating signed cookies');
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
