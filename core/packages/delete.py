import os
import json
import boto3

def delete(event, context):

    print(json.dumps(event))
    print('Auth Token: ' + event['headers']['Authorization'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('COGNITO_DOMAIN: ' + os.environ['COGNITO_DOMAIN'])
    username = event['requestContext']['authorizer']['claims']['profile'].split('/')[3]
    print('Username: ' + username)
    print('Id: ' + event['pathParameters']['id'])
    print()

    # Remove pypi assets for this package
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(os.environ['PYPI_BUCKET_NAME'])
    for key in bucket.objects.filter(Prefix=event['pathParameters']['id'] + '/'):
        print(key)
        key.delete()

    # Remove DynamoDB entry
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    table.delete_item(
        Key={
            'package': event['pathParameters']['id']
        }
    )

    # create a response
    retVal = {}
    retVal["from"] = 'delete'
    retVal["id"] = event['pathParameters']['id']
    response = {
        "statusCode": 200,
        "headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(retVal)
    }

    return response
