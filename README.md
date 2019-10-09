
# AWS Big Data - Applications

This repository provides an assortment of AWS Big Data example stacks, which are all delivered as infrastructure as code.

## firehose

The stack demonstrates how to use Firehose to stream logs from EC2 instances to an S3 bucket.

The stack includes the following components:

* Simple EC2 instance with Apache web server and CRON jobs to generate continuous traffic in the Apache access logs
* Kinesis Agent on the EC2 instance LOGTOJSON pre-processing configuration
* Firehose delivery stream
* Lambda trigger to demonstrate transformation of log events on the delivery stream (translate Apache timestamp "datetime" field to ISO 8601 and add as new field "datetimeiso")
* S3 log record destination bucket
* A reasonable amount of encryption at rest with encryption of the origin EC2 instance EBS volume and the destination S3 bucket objects emanating from Firehose

# Deployment

## Prerequisites

You will need an AWS account and an IAM user (or role or AWS SSO configuration) with valid AWS credentials. The user should have permissions to create resources in the account.

You will also need to deploy the [AWS Landing Zone core stack](https://github.com/virtuability/aws-lz).

All source code is developed in Python 3(.7) and you will need to install the Python 3.7 runtime to perform local development and tests.

You will also need the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli), [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and ideally [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint) too.

You can install the CLI tools in the user context as follows:

```bash
pip install --user --upgrade awscli aws-sam-cli cfn-lint
```

## Setup

An S3 staging bucket is needed to store AWS SAM & Cloudformation artifacts.

Create the bucket as follows:

```bash
# Validate credentials and get account
DEPLOY_ACCOUNT=`aws sts get-caller-identity | jq -r '.Account'`

# Set the default region to run the examples in
AWS_DEFAULT_REGION=eu-west-1

# Create staging bucket for Cloudformation, builds etc
STAGING_BUCKET=staging-${AWS_DEFAULT_REGION}-${DEPLOY_ACCOUNT}

aws s3 mb s3://${STAGING_BUCKET}
```

## Deploy app stack

Preparation:

```bash
# Set environment variables
GIT_DIR=$HOME/ldev/git/virtuability/aws-big-data
DEPLOY_ACCOUNT=`aws sts get-caller-identity | jq -r '.Account'`
AWS_DEFAULT_REGION=eu-west-1
STAGING_BUCKET=staging-${AWS_DEFAULT_REGION}-${DEPLOY_ACCOUNT}

# Optionally disable SAM CLI telemetry
SAM_CLI_TELEMETRY=0

# Choose app and environment to build and deploy
DEPLOY_APP=firehose
DEPLOY_ENV=development

cd $GIT_DIR/$DEPLOY_APP
```

Build the app stack template:

```bash
# Validate template
cfn-lint template.yaml

sam build --base-dir . --build-dir target/ --template template.yaml

sam package --template-file target/template.yaml \
  --s3-bucket ${STAGING_BUCKET} \
  --s3-prefix ${DEPLOY_APP} \
  --output-template-file target/${DEPLOY_APP}-${DEPLOY_ENV}.packaged
```

Deploy the app stack (**note that the resources will cost money**).

```bash
aws cloudformation create-stack --stack-name ${DEPLOY_APP}-${DEPLOY_ENV} \
  --template-body file://$GIT_DIR/$DEPLOY_APP/target/${DEPLOY_APP}-${DEPLOY_ENV}.packaged \
  --parameters file://$GIT_DIR/$DEPLOY_APP/parameters/${DEPLOY_ENV}.json \
  --tags Key=application,Value=$DEPLOY_APP Key=environment,Value=${DEPLOY_ENV} \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

Update the stack:

```bash
aws cloudformation update-stack --stack-name ${DEPLOY_APP}-${DEPLOY_ENV} \
  --template-body file://$GIT_DIR/$DEPLOY_APP/target/${DEPLOY_APP}-${DEPLOY_ENV}.packaged \
  --parameters file://$GIT_DIR/$DEPLOY_APP/parameters/${DEPLOY_ENV}.json \
  --tags Key=application,Value=$DEPLOY_APP Key=environment,Value=${DEPLOY_ENV} \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

Delete the stack:

```bash
aws cloudformation delete-stack --stack-name ${DEPLOY_APP}-${DEPLOY_ENV}
```
