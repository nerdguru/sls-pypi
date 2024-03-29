import os
import boto3

def dynamoPackage(event, context):
    # Echo inputs
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('WEB_TOPIC_ARN: ' + os.environ['WEB_TOPIC_ARN'])
    print('WEB_ROOT_TOPIC_ARN: ' + os.environ['WEB_ROOT_TOPIC_ARN'])
    print('REMOVE_WEB_TOPIC_ARN: ' + os.environ['REMOVE_WEB_TOPIC_ARN'])
    print('Event: ' + event['Records'][0]['eventName'])

    if event['Records'][0]['eventName'] == 'REMOVE':
        print('Remove record:')
        print(event['Records'][0]['dynamodb']['OldImage']['package']['S'])
        sns = boto3.client('sns')
        response = sns.publish(
            TopicArn=os.environ['REMOVE_WEB_TOPIC_ARN'],
            Message=event['Records'][0]['dynamodb']['OldImage']['package']['S'],
        )
        print(response)
    else:
        # Add message to SNS topic that'll force a refresh of the package page page
        print('Add or modify record:')
        print(event['Records'][0]['dynamodb']['NewImage']['package']['S'])
        sns = boto3.client('sns')
        response = sns.publish(
            TopicArn=os.environ['WEB_TOPIC_ARN'],
            Message=event['Records'][0]['dynamodb']['NewImage']['package']['S'],
        )
        print(response)
        # Add message to SNS topic that'll force a refresh of the home page
        response = sns.publish(
            TopicArn=os.environ['WEB_ROOT_TOPIC_ARN'],
            Message='Refresh, ' + event['Records'][0]['dynamodb']['NewImage']['package']['S'] + 'added/updated',
        )
        print(response)

    return
