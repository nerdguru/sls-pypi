import json
import os
import boto3
from github import Github
from s3pypi import __prog__, __version__
from s3pypi.exceptions import S3PyPiError
from s3pypi.package import Package
from s3pypi.storage import S3Storage
import shutil
import subprocess

# recursive download per https://sookocheff.com/post/tools/downloading-directories-of-code-from-github-using-the-github-api/
def download_folder(repository, rep_path, target_path):
    contents = repository.get_dir_contents(rep_path)

    for content in contents:
        print('Processing ',  content.path)
        if content.type == 'dir':
            if not os.path.isdir(target_path + content.path):
                os.makedirs(target_path + content.path)
            download_folder(repository, content.path, target_path)
        else:
            try:
                path = content.path
                file_content = repository.get_contents(path)
                file_data = file_content.decoded_content.decode("utf-8")
                file_out = open(target_path + content.path, "w+")
                file_out.write(file_data)
                file_out.close()
            except (Exception) as ex:
                print('Error processing ', content.path, str(ex))

# Per https://github.com/novemberfiveco/s3pypi/blob/master/s3pypi/__main__.py
def create_and_upload_package(bucket, package):
    package = Package.create(dist_path='/tmp/' + package + '/dist')
    storage = S3Storage(bucket)

    index = storage.get_index(package)
    index.add_package(package)

    storage.put_package(package)
    storage.put_index(package, index)

def get_secret(key):
    ssm = boto3.client('ssm')
    resp = ssm.get_parameter(Name=key, WithDecryption=True)
    return resp['Parameter']['Value']

def run_command(cmd_str):
    MyOut = subprocess.Popen(cmd_str.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()
    return(stdout.decode("utf-8"))

def publish(event, context):

    print(json.dumps(event))
    print('Auth Token: ' + event['headers']['Authorization'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('COGNITO_DOMAIN: ' + os.environ['COGNITO_DOMAIN'])
    username = event['requestContext']['authorizer']['claims']['profile'].split('/')[3]
    print('Username: ' + username)
    print('Id: ' + event['pathParameters']['id'])
    access_token = get_secret('GitHubAccessToken')
    print('Access token: ' + access_token)
    print()

    # First check to make sure the ID doesn't collide with "my"
    if(event['pathParameters']['id'] == 'my'):
        print('409 return, attempt to publish a package named my')
        response = {
            "statusCode": 409,
            "headers": { 'Access-Control-Allow-Origin': '*' },
            "body": 'Package name collides with a reserved name, please choose another name'
        }
        return response

    # Now check with the packages table for another collision
    dynamodb = boto3.resource('dynamodb')
    packages_table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    packages_result = packages_table.scan()
    package_list = []
    for item in packages_result['Items']:
        if item['package'] == event['pathParameters']['id']:
            if item['author'] != username:
                print('409 return, attempt to publish a package whose name collides with one already submitted by another user')
                response = {
                    "statusCode": 409,
                    "headers": { 'Access-Control-Allow-Origin': '*' },
                    "body": 'Package name collides with a package owned by another user, please choose another name'
                }
                return response


    # Load the package into the pypi bucket
    target_path = '/tmp/' + event['pathParameters']['id'] + '/'
    print('Target path: ' + target_path)
    # First, download the repo in question
    github_name = username + '/' + event['pathParameters']['id']
    g = Github(access_token)
    repo = g.get_repo(github_name)
    print(repo)
    download_folder(repo, '.', target_path)

    # Now publish to bucket
    print(os.getcwd())
    os.chdir(target_path)
    print(os.getcwd())
    try:
        print(run_command('ls -l .'))
        print(run_command('python3 setup.py sdist --formats gztar'))
        print(run_command('ls -l .'))
        create_and_upload_package(os.environ['PYPI_BUCKET_NAME'], event['pathParameters']['id'])
    except S3PyPiError as e:
        print("error: %s" % e)

    # Clean up
    # Delete all contents of a directory using shutil.rmtree() and  handle exceptions
    try:
       shutil.rmtree(target_path)
    except:
       print('Error while deleting directory')

    # Write author/package to database table
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
