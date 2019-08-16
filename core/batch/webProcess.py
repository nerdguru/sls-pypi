import os
import boto3
from github import Github
import markdown2
import requests
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

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
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
    print('FOOTER_TEXT: ' + os.environ['FOOTER_TEXT'])
    print('HEADER_SUBTEXT: ' + os.environ['HEADER_SUBTEXT'])
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

    # HEADERTEXT
    output = output.replace('HEADERTEXT', os.environ['WEB_BUCKET_NAME'] + ' - ' + os.environ['HEADER_SUBTEXT'])

    # PACKAGENAME
    output = output.replace('PACKAGENAME', package)

    # README_CONTENT
    g = Github(access_token)
    repo = g.get_repo(github_name)
    readme_contents = repo.get_readme()
    md_no_first = readme_contents.decoded_content.decode("utf-8").split("\n",1)[1]
    #print(md_no_first)
    readme_md = markdown2.markdown(md_no_first,extras=["fenced-code-blocks"])
    output = output.replace('README_CONTENT', readme_md)

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
    versions_string = ''
    pypi_bucket = s3.Bucket(os.environ['PYPI_BUCKET_NAME'])
    for obj in pypi_bucket.objects.filter(Prefix=package):
        print(obj.key)
        if obj.key.endswith('.tar.gz'):
            version = obj.key.replace('.tar.gz','').replace(package + '/' + package + '-','')
            print(version)
            if versions_string == '':
                versions_string += version
            else:
                versions_string += ', ' + version
    output = output.replace('VERSIONS', versions_string)

    # DEPENDENTS_CONTENT
    dependents_raw_html = simple_get('https://github.com/' + github_name + '/network/dependents')
    dependents_soup = BeautifulSoup(dependents_raw_html, 'html.parser')
    dependents_divs = dependents_soup.findAll("div", {"class": "Box-header"})
    dependent_packages = 0
    dependent_repos = 0
    for div in dependents_divs:
        btn = div.findAll("a", {"class": "btn-link"})
        dep_parts = btn[0].contents[2].split("\n")
        pack_parts = btn[1].contents[2].split("\n")
        dependent_packages = int(pack_parts[1].replace(",",""))
        dependent_repos = int(dep_parts[1].replace(",",""))

    dependents_string = '<a href="https://github.com/' + github_name + '/network/dependents" target="_blank">' + str(dependent_packages) + ' packages</br>\n'+ str(dependent_repos) + ' repositories</a>'
    output = output.replace('DEPENDENTS_CONTENT', dependents_string)

    # DEPENDENCIES_CONTENT
    dependencies_raw_html = simple_get('https://github.com/' + github_name + '/network/dependencies')
    dependencies_soup = BeautifulSoup(dependencies_raw_html, 'html.parser')
    dependencies_divs = dependencies_soup.findAll("div", {"class": "table-list-header-toggle"})
    total_dependencies = 0
    for div in dependencies_divs:
        dep_parts = div.findAll("span", {"class": "Counter"})[0].contents[0].split("\n")
        total_dependencies += int(dep_parts[1].replace(",",""))

    dependencies_string = '<a href="https://github.com/' + github_name + '/network/dependencies" target="_blank">' + str(total_dependencies) + ' packages</a>'
    output = output.replace('DEPENDENCIES_CONTENT', dependencies_string)

    # LICENSE
    url = 'https://api.github.com/repos/' + github_name + '/license'
    headers = {'Authorization': 'token' + access_token}
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        output = output.replace('LICENSE', 'none')
    else:
        output = output.replace('LICENSE', r.json()["license"]["name"])

    # OPENISSUES
    open_issues = repo.get_issues(state='open')
    open_issues_string = '<a href="https://github.com/' + github_name + '/issues" target="_blank">' + str(open_issues.totalCount) + '</a>'
    output = output.replace('OPENISSUES', open_issues_string)

    # PULLREQUESTS
    pulls = repo.get_pulls(state='open', sort='created', base='master')
    pull_requests_string = '<a href="https://github.com/' + github_name + '/pulls" target="_blank">' + str(pulls.totalCount) + '</a>'
    output = output.replace('PULLREQUESTS', pull_requests_string)

    # GITHUBREPO
    repo_string = '<a href="https://github.com/' + github_name + '" target="_blank">' + github_name + '</a>'
    output = output.replace('GITHUBREPO', repo_string)

    # CONTRIBUTORS
    contributors = repo.get_contributors()
    contributors_string = '<a href="https://github.com/' + github_name + '/graphs/contributors" target="_blank">' + str(contributors.totalCount) + '</a>'
    output = output.replace('CONTRIBUTORS', contributors_string)

    # FOOTERTEXT
    output = output.replace('FOOTERTEXT', os.environ['FOOTER_TEXT'])

    # Write out the results
    print('Find/replace complete, writing: ' + package)
    out_obj = s3.Object(os.environ['WEB_BUCKET_NAME'], package + '/index.html')
    out_obj.put(Body=output,ContentType='text/html', ACL='public-read')

    return
