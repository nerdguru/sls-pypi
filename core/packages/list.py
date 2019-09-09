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

def removeDuplicates(listofElements):

    # Create an empty list to store unique elements
    uniqueList = []

    # Iterate over the original list and for each element
    # add it to uniqueList, if its not already there.
    for elem in listofElements:
        if elem not in uniqueList:
            uniqueList.append(elem)

    # Return the list of unique elements
    return uniqueList

def list(event, context):

    access_token = get_secret('GitHubAccessToken')
    print('Access token: ' + access_token)
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
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

    # Get the list of repos matching this authorized user
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
    package_list.sort()
    s3 = boto3.resource('s3')
    for item in package_list:
        retItem = {}
        retItem["package"] = item
        retItem["versions"]=[]
        pypi_bucket = s3.Bucket(os.environ['PYPI_BUCKET_NAME'])
        for obj in pypi_bucket.objects.filter(Prefix=item):
            print(obj.key)
            if obj.key.endswith('.tar.gz'):
                version = obj.key.replace('.tar.gz','').replace(item + '/' + item + '-','')
                print(version)
                retItem["versions"].append(version)

        retItem["downloads"] = {}
        web_table = dynamodb.Table(os.environ['WEB_DYNAMODB_TABLE'])
        web_result = web_table.scan()
        downloads = 0
        locations = []
        requestIPs = []
        for web_log_item in web_result['Items']:
            if web_log_item['package'] == item:
                downloads += 1
                locations.append(web_log_item['location'])
                requestIPs.append(web_log_item['requestIP'])
        retItem["downloads"]["number"] = downloads
        retItem["downloads"]["locations"] = len(removeDuplicates(locations))
        retItem["downloads"]["requestIPs"] = len(removeDuplicates(requestIPs))
        submitted_packages.append(retItem)

	# Build structure for submitted packages
    unsubmitted_packages = potentials
    for item in potentials:
 	    print(item)
 	    matches = False

 	    for package in submitted_packages:
 	        print('Package: ' + package["package"]  + ' Item: ' + item)
 	        if package["package"]  == item:
 	            unsubmitted_packages.remove(item)

	# create a response
    retVal = {}
    retVal["submitted"] = submitted_packages
    retVal["unsubmitted"] = unsubmitted_packages
    response = {
        "statusCode": 200,
		"headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(retVal)
    }

    return response
