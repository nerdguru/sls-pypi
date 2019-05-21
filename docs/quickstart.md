# Serverless PyPi Quickstart

The following are requirements for installing Serverles PyPi:

* An AWS Account
* The AWS cli installed
* A base domain name created in Route53
* The Serverless Framework installed

The installation requires two steps.

## Step 1: Installing Custom CloudFormation Resource Providers
Not all assets required to operate Serverles Pypi can be created and integrated
with one another with standard  CloudFormation constructs.  During this step,
a set of custom CloudFormation Resource Providers will be installed that fill
in the gaps.

Start this process by getting in the correct directory, selecting a bucket name
to store the zip files that house the custom Resource Providers, and copying the
zip files to the bucket:
```
cd custom-cloudformation
read -p "custom Resource Provider Bucket Name: " BUCKET_NAME
aws s3 mb s3://$BUCKET_NAME
aws s3 cp cfn-certificate-provider-0.2.4.zip s3://$BUCKET_NAME
aws s3 cp cfn-cognito-user-pools.zip s3://$BUCKET_NAME
```
Then, deploy the custom Resource Providers
```
aws cloudformation create-stack \
	--capabilities CAPABILITY_NAMED_IAM \
	--stack-name sls-pypi-cf-resource-providers \
	--template-body file://custom-resource-providers.yaml \
    --parameters ParameterKey=ResourceBucketName,ParameterValue=$BUCKET_NAME
```
## Step 2: Installing the Core
```
cd ../core
sls deploy
```
