import os
import boto3
import re
import uuid
from urllib.parse import unquote

def writeWebLogs(event, context):
    # Echo inputs
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
    print('WEB_TOPIC_ARN: ' + os.environ['WEB_TOPIC_ARN'])
    print('Triggering bucket: ' + event['Records'][0]['s3']['bucket']['name'])
    print('Triggering object: ' + event['Records'][0]['s3']['object']['key'])

    # Read in the object in question
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=event['Records'][0]['s3']['bucket']['name'],
                         Key=event['Records'][0]['s3']['object']['key'])
    data = response['Body'].read().decode('utf-8')

    # Now process the lines
    package = ''
    lines = data.split('\n')
    first = True
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['WEB_DYNAMODB_TABLE'])
    for line in lines:
        # Skip the first line
        print(line)
        if not first:
            columns = line.split('","')
            # Only process non-blank lines
            if len(columns) > 1:
                dlDate = columns[0].replace('"','')
                dlTime = columns[1]
                dlLocation = columns[2]
                dlReqIP =  columns[4]
                uri = columns[7].replace('.tar.gz','')
                uri = uri.replace('.whl','')
                uri = uri.replace('-',' ')
                uri = re.sub('/.*?/', '', uri)
                packVer = uri.split(' ')
                dlPackage = packVer[0]
                package = dlPackage
                dlVersion = packVer[1]
                print(unquote(unquote(columns[10])))
                dlAgent = unquote(unquote(columns[10]))
                print(dlDate + ' ' + dlTime + ' ' + dlLocation + ' ' + dlReqIP + ' ' + dlPackage + ' ' + dlVersion + ' ' + dlAgent)

                item = {
                    'id': dlPackage + '-' + dlDate + '-' + dlTime + '-' + dlReqIP,
                    'package': dlPackage,
                    'date': dlDate,
                    'time': dlTime,
                    'location': dlLocation,
                    'requestIP': dlReqIP,
                    'version': dlVersion,
                    'agent': dlAgent,
                }
                table.put_item(Item=item)

        first = False

    # Now publish the SNS message to kick off web processing
    if package:
        sns = boto3.client('sns')
        print('Found package: ' + package)
        response = sns.publish(
            TopicArn=os.environ['WEB_TOPIC_ARN'],
            Message=package,
        )
        print(response)

    return
