import os
import boto3
import time

def athenaQuery(event, context):
    # Echo inputs
    print('Package:  ' + event['Records'][0]['Sns']['Message'])
    print('QUERY_RESULTS_BUCKET_NAME: ' + os.environ['QUERY_RESULTS_BUCKET_NAME'])
    print('ATHENA_DB_NAME: ' + os.environ['ATHENA_DB_NAME'])
    print('ATHENA_TABLE_NAME: ' + os.environ['ATHENA_TABLE_NAME'])
    print('TIMEOUT: ' + os.environ['TIMEOUT'])

    # Construct query
    query = 'SELECT * FROM "' + os.environ['ATHENA_DB_NAME'] + '"."' + os.environ['ATHENA_TABLE_NAME'] + '"'
    query += ' WHERE "status" = 200'
    query += ' AND ("uri" LIKE \'%.gz\' OR "uri" LIKE \'%.whl\')'
    query += ' AND "uri" LIKE \'%/' + event['Records'][0]['Sns']['Message'] + '/%\''
    query += ' ORDER BY date ASC, time ASC'
    print('Query created: ' + query)

    # Set up client
    client = boto3.client('athena')
    print('Client initialized')

    # Query
    response = client.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': 's3://' + os.environ['QUERY_RESULTS_BUCKET_NAME']
        }
    )
    execution_id = response['QueryExecutionId']
    print('Query executed with ID: ' + execution_id)

    # Now check on status
    state = 'RUNNING'
    max_execution = int(os.environ['TIMEOUT'])
    while (max_execution > 0 and state in ['RUNNING']):
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId = execution_id)

        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            print('Query ' + execution_id + ' state: ' + state)
            if state == 'FAILED':
                print('Failed query state, check Athena history')
                raise Exception('Failed query state, check Athena history')
        time.sleep(1)

    if(max_execution == 0):
        print('Function internal timeout threshold exceeded')
        raise Exception('Function internal timeout threshold exceeded')

    return
