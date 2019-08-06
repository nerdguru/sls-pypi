import os
import boto3

def webRemove(event, context):
    # Echo inputs
    print('Package: ' + event['Records'][0]['Sns']['Message'])
    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])

    return
