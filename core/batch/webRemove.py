import os
import boto3

def webRemove(event, context):
    # Echo inputs
    print('Package: ' + event['Records'][0]['Sns']['Message'])
    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])
    print('WEB_ROOT_TOPIC_ARN: ' + os.environ['WEB_ROOT_TOPIC_ARN'])

    # Remove web assets for this package
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(os.environ['WEB_BUCKET_NAME'])
    for key in bucket.objects.filter(Prefix=event['Records'][0]['Sns']['Message'] + '/'):
        print(key)
        key.delete()

    # Add message to SNS topic that'll force a refresh of the home page
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=os.environ['WEB_ROOT_TOPIC_ARN'],
        Message='Refresh, ' + event['Records'][0]['Sns']['Message'] + 'deleted',
    )
    print(response)

    return
