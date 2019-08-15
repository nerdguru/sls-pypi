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

## Step 1: Installing Custom CloudFormation Resource Providers
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
Then, deploy the custom Resource Providers
```
aws cloudformation create-stack \
	--capabilities CAPABILITY_NAMED_IAM \
	--stack-name sls-pypi-cf-resource-providers \
	--template-body file://custom-cf/custom-resource-providers.yaml \
    --parameters ParameterKey=ResourceBucketName,ParameterValue=$BUCKET_NAME
```
## Step 2: Issuing and Validating the HTTPS Certificate
The command line `pip` client requires communication with any back end index repository via HTTPS, which an S3 bucket acting as a static HTTP server cannot support on its own.  Instead, CloudFront can act as the HTTPS front end provided it has a valid certificate.  This step issues that certificate using AWS Certificate Manager and validates it using the DNS record method.

A prerequisite of this step is that a base domain name is being managed by Route 53.  That base domain name and the Hosted Zone ID referencing it in Route 53 are used below.
```
read -p "domain name: " DOMAIN_NAME
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
## Step 4: Installing the core components
sls-pypi core components require a GitHub access token with repo:public_repo and the AWS Systems Manager is used to manage that access token securely.  In order for the deployment process to set that access token, open the `github.template` file in the `core` folder, replace the value so that it contains your access token, and save the result as `github.yml`.  Alternatively, set the key to a bogus value for deployment and after the deployment step below completes, manually set the access token in the AWS Systems Manager console.

Then perform the following in the `core` folder:
```
sls deploy
```
## Step 5: Installing and Configuring Oauth

## Step 6: Testing the deployment
