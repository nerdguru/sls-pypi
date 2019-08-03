import os
import boto3

def webProcess(event, context):
    # Echo inputs
    print('TEMPLATES_BUCKET_NAME: ' + os.environ['TEMPLATES_BUCKET_NAME'])
    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])

    return
