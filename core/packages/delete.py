import os
import json
import boto3

def delete(event, context):
    #table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # delete the todo from the database
    # dynamodb = boto3.resource('dynamodb')
    # table.delete_item(
    #     Key={
    #         'id': event['pathParameters']['id']
    #     }
    # )

    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    username = os.environ['USERNAME']
    print('Username: ' + username)
    print('Id: ' + event['pathParameters']['id'])
    print()

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
