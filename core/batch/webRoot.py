import os
import boto3

def webRoot(event, context):
    # Echo inputs
    print('TEMPLATES_BUCKET_NAME: ' + os.environ['TEMPLATES_BUCKET_NAME'])
    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('PACKAGES_DYNAMODB_TABLE: ' + os.environ['PACKAGES_DYNAMODB_TABLE'])
    print('WEB_DYNAMODB_TABLE: ' + os.environ['WEB_DYNAMODB_TABLE'])
    print('FOOTER_TEXT: ' + os.environ['FOOTER_TEXT'])
    print('HEADER_SUBTEXT: ' + os.environ['HEADER_SUBTEXT'])
    print()

    # Build list of all packages
    dynamodb = boto3.resource('dynamodb')
    packages_table = dynamodb.Table(os.environ['PACKAGES_DYNAMODB_TABLE'])
    packages_result = packages_table.scan()
    package_list = []

    for item in packages_result['Items']:
        print('Package: ' + item['package'])
        package_list.append(item['package'])

    package_list.sort()

    listA=''
    listB=''
    listC=''
    current_list = 'A'
    for package in package_list:
        list_item = '<li><a href="/' + package + '">' + package + '</a></li>\n'
        if current_list == 'A':
            listA += list_item
            current_list = 'B'
        elif current_list == 'B':
            listB += list_item
            current_list = 'C'
        else:
            listC += list_item
            current_list = 'A'

    # Get the template file
    s3 = boto3.resource('s3')
    obj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'home.html')
    output = obj.get()['Body'].read().decode('utf-8')

    # SITENAME
    output = output.replace('SITENAME', os.environ['WEB_BUCKET_NAME'])

    # HEADERTEXT
    output = output.replace('HEADERTEXT', os.environ['WEB_BUCKET_NAME'] + ' - ' + os.environ['HEADER_SUBTEXT'])

    # LISTA, LISTB, LISTC
    output = output.replace('LISTA', listA)
    output = output.replace('LISTB', listB)
    output = output.replace('LISTC', listC)

    # FOOTERTEXT
    output = output.replace('FOOTERTEXT', os.environ['FOOTER_TEXT'])

    # Write out the results
    print('Find/replace complete, writing: site root')
    out_obj = s3.Object(os.environ['WEB_BUCKET_NAME'], 'index.html')
    out_obj.put(Body=output,ContentType='text/html', ACL='public-read')

    return
