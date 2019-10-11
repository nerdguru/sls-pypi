import os
import json
import boto3
import urllib

def csv(event, context):
    print(json.dumps(event))
    print('Auth Token: ' + event['headers']['Authorization'])
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
    print('COGNITO_DOMAIN: ' + os.environ['COGNITO_DOMAIN'])
    username = event['requestContext']['authorizer']['claims']['profile'].split('/')[3]
    print('Username: ' + username)
    print('Id: ' + event['pathParameters']['id'])
    print()

    # Query the web log Table
    dynamodb = boto3.resource('dynamodb')
    web_table = dynamodb.Table(os.environ['WEB_DYNAMODB_TABLE'])
    web_result = web_table.scan()
    csv = ''
    csv = 'package' + ',' + 'version' + ',' + 'date' + ',' + 'time' + ',' + 'location' + ',' + 'requestIP\r\n'
    for item in web_result['Items']:
        if item['package'] == event['pathParameters']['id']:
            csv += item['package'] + ',' + item['version'] + ',' + item['date'] + ',' + item['time'] + ',' + item['location'] + ',' + item['requestIP'] + '\r\n'

    # create a response
    retVal = {}
    retVal["csv"] = urllib.parse.quote(csv);
    response = {
        "statusCode": 200,
        "headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(retVal)
    }

    return response
