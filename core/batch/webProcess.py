import os
import boto3

ssm = boto3.client('ssm')
def get_secret(key):
	resp = ssm.get_parameter(
		Name=key,
		WithDecryption=True
	)
	return resp['Parameter']['Value']

def webProcess(event, context):

    package = event['Records'][0]['Sns']['Message']

    print('TEMPLATES_BUCKET_NAME: ' + os.environ['TEMPLATES_BUCKET_NAME'])
    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
    access_token = get_secret('GitHubAccessToken')
    print('Access token: ' + access_token)
    print()

    # Now find the author
    dynamodb = boto3.resource('dynamodb')
    packages_table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    packages_result = packages_table.scan()
    author = ''
    for item in packages_result['Items']:
        if item['package'] == package:
            author = item['author']
    github_name = author + '/' + package
    print('Author: ' + author)
    print('Github name:' + github_name)
    print('Package: ' + package)
    print()

    # Get the template file
    s3 = boto3.resource('s3')
    obj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'package.html')
    output = obj.get()['Body'].read().decode('utf-8')
    #print(output)

    # SITENAME
    output = output.replace('SITENAME', os.environ['WEB_BUCKET_NAME'])

    # PACKAGENAME
    output = output.replace('PACKAGENAME', package)

    # DOWNLOADS
    web_table = dynamodb.Table(os.environ['WEB_DYNAMODB_TABLE'])
    web_result = web_table.scan()
    downloads = 0
    for item in web_result['Items']:
        if item['package'] == package:
            downloads += 1
    print('Downloads: ' + str(downloads))
    output = output.replace('DOWNLOADS', str(downloads))

    # VERSIONS


    # GITHUBREPO
    repo_string = '<a href="https://github.com/' + github_name + '" target="_blank">' + github_name + '</a>'
    output = output.replace('GITHUBREPO', repo_string)

    # Write out the results
    print('Find/replace complete, writing: ' + package)
    out_obj = s3.Object(os.environ['WEB_BUCKET_NAME'], package + '/index.html')
    out_obj.put(Body=output,ContentType='text/html', ACL='public-read')

    return
