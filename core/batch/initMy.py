import os
import boto3

def initMy(event, context):

    print('WEB_BUCKET_NAME: ' + os.environ['WEB_BUCKET_NAME'])
    print('TEMPLATES_BUCKET_NAME: ' + os.environ['TEMPLATES_BUCKET_NAME'])
    print('PYPI_BUCKET_NAME: ' + os.environ['PYPI_BUCKET_NAME'])
    print('HEADER_SUBTEXT: ' + os.environ['HEADER_SUBTEXT'])
    print('USERPOOL_ID: ' + os.environ['USERPOOL_ID'])
    print('CLIENT_ID: ' + os.environ['CLIENT_ID'])
    print('COGNITO_DOMAIN: ' + os.environ['COGNITO_DOMAIN'])
    print('API_CORE: ' + os.environ['API_CORE'])
    print('API_REMAINDER: ' + os.environ['API_REMAINDER'])
    apiUrl = 'https://' + os.environ['API_CORE'] + os.environ['API_REMAINDER']
    print('API URL: ' + apiUrl)
    print()

    # Get the template my file
    s3 = boto3.resource('s3')
    myObj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'my.html')
    myOutput = myObj.get()['Body'].read().decode('utf-8')

    # SITENAME
    myOutput = myOutput.replace('SITENAME', os.environ['WEB_BUCKET_NAME'])

    # HEADERTEXT
    myOutput = myOutput.replace('HEADERTEXT', os.environ['WEB_BUCKET_NAME'] + ' - ' + os.environ['HEADER_SUBTEXT'])

    print('Find/replace complete on my.html, writing')
    my_out_obj = s3.Object(os.environ['PYPI_BUCKET_NAME'], 'my/index.html')
    my_out_obj.put(Body=myOutput,ContentType='text/html', ACL='public-read')

    # Get the template amazon-cognito-auth.min.js file
    jsObj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'amazon-cognito-auth.min.js')
    jsOutput = jsObj.get()['Body'].read().decode('utf-8')

    print('amazon-cognito-auth.min.js, writing')
    js_out_obj = s3.Object(os.environ['PYPI_BUCKET_NAME'], 'my/amazon-cognito-auth.min.js')
    js_out_obj.put(Body=jsOutput,ContentType='application/javascript', ACL='public-read')

    # Get the template amazon-cognito-auth.min.js.map file
    mapObj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'amazon-cognito-auth.min.js.map')
    mapOutput = mapObj.get()['Body'].read().decode('utf-8')

    print('amazon-cognito-auth.min.js.map, writing')
    map_out_obj = s3.Object(os.environ['PYPI_BUCKET_NAME'], 'my/amazon-cognito-auth.min.js.map')
    map_out_obj.put(Body=mapOutput,ContentType='application/javascript', ACL='public-read')

    # Get the template packageManagementHelp.html file
    helpObj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'packageManagementHelp.html')
    helpOutput = helpObj.get()['Body'].read().decode('utf-8')

    print('packageManagementHelp.html, writing')
    help_out_obj = s3.Object(os.environ['PYPI_BUCKET_NAME'], 'my/packageManagementHelp.html')
    help_out_obj.put(Body=helpOutput,ContentType='text/html', ACL='public-read')


    # Get the template rest.js file
    s3 = boto3.resource('s3')
    restObj = s3.Object(os.environ['TEMPLATES_BUCKET_NAME'], 'rest.js')
    restOutput = restObj.get()['Body'].read().decode('utf-8')

    # DOMAIN
    restOutput = restOutput.replace('CORE_DOMAIN', os.environ['WEB_BUCKET_NAME'])

    # COGNITO_DOMAIN
    restOutput = restOutput.replace('COGNITO_DOMAIN', os.environ['COGNITO_DOMAIN'])

    # USERPOOL_ID
    restOutput = restOutput.replace('USERPOOL_ID', os.environ['USERPOOL_ID'])

    # CLIENT_ID
    restOutput = restOutput.replace('CLIENT_ID', os.environ['CLIENT_ID'])

    # API_PATH
    restOutput = restOutput.replace('API_PATH', apiUrl)

    print('Find/replace complete on rest.js, writing')
    rest_out_obj = s3.Object(os.environ['PYPI_BUCKET_NAME'], 'my/rest.js')
    rest_out_obj.put(Body=restOutput,ContentType='application/javascript', ACL='public-read')
