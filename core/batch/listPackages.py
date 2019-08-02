import os
import boto3
import json

def listPackages(event, context):
    # Echo inputs
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('ATHENA_TOPIC_ARN: ' + os.environ['ATHENA_TOPIC_ARN'])

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])

    # fetch all packages from the database
    result = table.scan()

    # Now place each one on the SNS topic
    sns = boto3.client('sns')
    for item in result['Items']:
        print('Found package: ' + item['package'])
        response = sns.publish(
            TopicArn=os.environ['ATHENA_TOPIC_ARN'],
            Message=item['package'],
        )
        print(response)

    return
