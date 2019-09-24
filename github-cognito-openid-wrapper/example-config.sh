#!/bin/bash -eu

# Variables always required
export GITHUB_CLIENT_ID=# <GitHub OAuth App Client ID>
export GITHUB_CLIENT_SECRET=# <GitHub OAuth App Client Secret>
export COGNITO_REDIRECT_URI=# https://<Your Cognito Domain>/oauth2/idpresponse

# Variables required if deploying with API Gateway / Lambda
export STACK_NAME=sls-pypi-github-cognito-openid-wrapper
export REGION=# AWS region to deploy the stack and bucket in
