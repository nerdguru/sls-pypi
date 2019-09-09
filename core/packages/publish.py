import json
import os
import boto3

def publish(event, context):
    # data = json.loads(event['body'])
    # if 'text' not in data:
    #     logging.error("Validation Failed")
    #     raise Exception("Couldn't create the todo item.")
    #     return
    #
    # timestamp = int(time.time() * 1000)
    #
    # table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    #
    # item = {
    #     'id': str(uuid.uuid1()),
    #     'text': data['text'],
    #     'checked': False,
    #     'createdAt': timestamp,
    #     'updatedAt': timestamp,
    # }
    #
    # # write the todo to the database
    # table.put_item(Item=item)
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    username = os.environ['USERNAME']
    print('Username: ' + username)
    print('Id: ' + event['pathParameters']['id'])
    print()

    # Load the package into the pypi bucket

    # Write author/package to database table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    item = {
        'package': event['pathParameters']['id'],
        'author': username,
    }
    table.put_item(Item=item)

    # create a response
    retVal = {}
    retVal["from"] = 'publish'
    retVal["id"] = event['pathParameters']['id']
    response = {
        "statusCode": 200,
        "headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(retVal)
    }

    return response
