# Serverless PyPi Quickstart

The following are requirements for installing Serverless PyPi:

* [An AWS Account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
* [The AWS cli installed](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* [The SAM cli installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [A base domain name registered in Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html)
* [The Serverless Framework installed](https://serverless.com/framework/docs/getting-started/)
* [An OAuth App created on GitHub](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/)
* [A GitHub access token](https://github.com/settings/tokens)

The installation requires six steps:

## Step 1: Installing Custom CloudFormation Resource Providers & Create the User Pool
Not all assets required to operate Serverles Pypi can be created and integrated
with one another with standard  CloudFormation constructs.  During this step,
a set of custom CloudFormation Resource Providers will be installed that fill
in the gaps.

Start this process from the root folder of the repo by selecting a bucket name
to store the zip files that house the custom Resource Providers and copying the
 relevant zip files to the bucket:
```
read -p "custom Resource Provider Bucket Name: " BUCKET_NAME
aws s3 mb s3://$BUCKET_NAME
aws s3 cp custom-cf/cfn-certificate-provider-0.2.4.zip s3://$BUCKET_NAME
aws s3 cp custom-cf/cfn-cognito-user-pools.zip s3://$BUCKET_NAME
```
Then, deploy the custom Resource Providers and create the User Pool:
```
read -p "domain name: " DOMAIN_NAME
aws cloudformation create-stack \
	--capabilities CAPABILITY_NAMED_IAM \
	--stack-name sls-pypi-cf-resource-providers \
	--template-body file://custom-cf/custom-resource-providers.yaml \
    --parameters ParameterKey=ResourceBucketName,ParameterValue=$BUCKET_NAME \
              ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME
```
## Step 2: Issuing and Validating the HTTPS Certificate
The command line `pip` client requires communication with any back end index repository via HTTPS, which an S3 bucket acting as a static HTTP server cannot support on its own.  Instead, CloudFront can act as the HTTPS front end provided it has a valid certificate.  This step issues that certificate using AWS Certificate Manager and validates it using the DNS record method.

A prerequisite of this step is that a base domain name is being managed by Route 53.  That base domain name and the Hosted Zone ID referencing it in Route 53 are used below.
```
read -p "hosted zone id: " HOSTED_ZONE
aws cloudformation create-stack --stack-name sls-pypi-certificate \
	--template-body file://cf/certificate.yaml \
	--parameters ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME \
		         ParameterKey=HostedZoneId,ParameterValue=$HOSTED_ZONE
```
Check the CloudFormation console and proceed only when this stack has been successfully deployed.  This should take on the order of 5 minutes and its outputs are dependencies for the next step.

## Step 3: Deploying the serverless Pypi index repository
With a valid certificate now available, this step will create an S3 bucket and a CloudFront distribution configured such that they create a valid HTTPS target for `pip`.
```
aws cloudformation create-stack --stack-name sls-pypi-index-repository \
    --template-body file://cf/index-repository.yaml \
    --capabilities CAPABILITY_IAM
```
This creates an S3 bucket named "pypi" + <domain name>, a CloudFront distribution
that fronts the bucket to provide HTTPS and is configured to log access to it,
and a DNS entry that points to the CloudFront distribution.  Completion time on
this step varies according to the CloudFront distribution setup, taking 30 minutes or longer.
## Step 4: Installing and Configuring Federated Login
To make for a better user experience, `sls-pypi` uses a federated login between Cognito
and GitHub.  Unfortunately, Cognito only supports OpenId and GitHub only supports OAuth,
so in order to get the two to talk to each other, `sls-pypi` utilizes [a shim written
by @JonesTim](https://github.com/TimothyJones/github-cognito-openid-wrapper).  Due to this complexity,
this is the lone step of the `sls-pypi` installation process that requires manual intervention.

The `sls-pypi` repo contains a copy of the @JomesTim as of September 24, 2019 in case he chooses
to shut down his shim project at some point.  Some of the set up steps described in his repo
are automated by Step 1, hence you may find differences between these instructions and his.

Specifically, Step 1 of these instructions automate the creation of the User Pool, the
User Pool Domain, and the App Client all within Cognito.  The manual steps described here
will be needed to set up the GitHub side of the shim, deploy the shim, and then configure the
Cognito side of the shim.

### Step 4a: Create a GitHub OAuth App
[Follow GitHub's instructions for creating a GitHub OAuth App ](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/).  Note that it needs to be an `OAuth App` not the default `GitHub App` when going into `Developer Settings`.  A `GitHub App` will not work.

As part of this process, you will be asked for your `Homepage URL` and your `Authorization callback URL`.  

For the `Homepage URL`, look in `CloudFormation` under the `sls-pypi-cf-resource-providers` stack.  Use the value `RedirectUriSignIn` in the `Outputs` tab of that stack, which should be something similar to `https://pypi.<your domain>/my`.

For the `Authorization callback URL`, in that same `sls-pypi-cf-resource-providers` stack, look for the `UserPoolDomainUrl` on the `Outputs` tab.  Use the value `<value of UserPoolDomainUrl>/oauth2/idpresponse`.  In other words, it should be your User Pool Domain with `/oauth2/idresponse` concatenated onto it.

Once done, make note of your `client ID` and `secret` as they will be used in the next sub step.

### Step 4b: Deploying the shim
Before being able to deploy the shim, certain configurations should be completed.  In a terminal window, `cd` into the `github-cognito-openid-wrapper` folder and perform the following:
```
cp example-config.sh config.sh
 vim config.sh # Or whatever your favourite editor is
```
This file has been modified compared to the original @JonesTim version given other environment variables already used in the `sls-pypi` process.  It should read:

```
#!/bin/bash -eu

# Variables always required
export GITHUB_CLIENT_ID=# <GitHub OAuth App Client ID>
export GITHUB_CLIENT_SECRET=# <GitHub OAuth App Client Secret>
export COGNITO_REDIRECT_URI=# https://<Your Cognito Domain>/oauth2/idpresponse

# Variables required if deploying with API Gateway / Lambda
export STACK_NAME=sls-pypi-github-cognito-openid-wrapper
export REGION=# AWS region to deploy the stack and bucket in
```
Under `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`, enter the `client id` and `secret` from the prior sub step.  For the `COGNITO_REDIRECT_URI`, enter the same URL performed in the prior sub step.  For `REGION`, set equal to the AWS region where `sls-pypi` is being deployed.

Once saved, deploy the shim with:

```
npm install
npm run deploy
```
This will download a variety of dependencies prior to performing the deployment.  Check `CloudFormationm` for its completion before proceeding to the next sub step.  Note the `Output` value of `XXX`, which will be used in the final sub step.

### Step 4c: Configuring OpenId

## Step 5: Installing the core components
sls-pypi core components require a GitHub access token with repo:public_repo and the AWS Systems Manager is used to manage that access token securely.  In order for the deployment process to set that access token, open the `github.template` file in the `core` folder, replace the value so that it contains your access token, and save the result as `github.yml`.  Alternatively, set the key to a bogus value for deployment and after the deployment step below completes, manually set the access token in the AWS Systems Manager console.

Then perform the following in the `core` folder:
```
sls deploy
```
This will deploy the final stack, including all the Lambda functions and IAM Roles/Permissions for the functions.
## Step 6: Testing the deployment
In order to test your deployment, see the two sample packages ([samples101](https://github.com/nerdguru/samples101) and [samples201](https://github.com/nerdguru/samples201)), copy them locally, create your own public repositories of the copy, and try to submit them.

## Congratulations!
You have now deployed `sls-pypi` successfully!  Future updates will likely not require all stacks to be re-deployed.  In most cases, only Step 5 will need to be repeated but check release notes for details.
