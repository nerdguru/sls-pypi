import json
from github import Github
import os
import boto3

ssm = boto3.client('ssm')
def get_secret(key):
	resp = ssm.get_parameter(
		Name=key,
		WithDecryption=True
	)
	return resp['Parameter']['Value']

def list(event, context):

    access_token = get_secret('GitHubAccessToken')
    print('Access token: ' + access_token)
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    username = os.environ['USERNAME']
    print('Username: ' + username)
    print()

    # Get the repos for this user and put potential packages in a a list
    g = Github(access_token)
    github_user = g.get_user(username)
    potentials = []
    for repo in github_user.get_repos():
        # Must be a Python repo
        if 'Python' in repo.language:
            contents = repo.get_contents("")
            for content_file in contents:
                # Also must have a setup.py in its root
                if content_file.path == 'setup.py':
                    potentials.append(repo.name)
    print(potentials)

    # Get the list of repos matching this authorized
    dynamodb = boto3.resource('dynamodb')
    packages_table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    packages_result = packages_table.scan()
    package_list = []
    for item in packages_result['Items']:
        if item['author'] == username:
            package_list.append(item['package'])
    print(package_list)

	# Build structure for submitted packages
    submitted_packages=[]
    for item in package_list:
        retItem = {}
        retItem["package"] = item
        retItem["versions"] = []
        retItem["downloads"] = {}
        retItem["downloads"]["number"] = 0
        retItem["downloads"]["pops"] = []
        retItem["downloads"]["sourceIps"] = []
        submitted_packages.append(retItem)

    unsubmitted_packages = []

    retVal = {}
    retVal["submitted"] = submitted_packages
    retVal["unsubmitted"] = unsubmitted_packages
    # create a response
    response = {
        "statusCode": 200,
		"headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(retVal)
    }

    return response
