import boto3
import botocore
from npm.bindings import npm_install
from flask import Flask, render_template, redirect, send_from_directory, request
import os
import datetime

app = Flask(__name__)

# Setting the credentials
aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

# Setting the AWS resources
s3 = boto3.resource('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)
dynamo = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_access_key)

# Installation of npm - app/pem
npm_install('app/pem')


# Rendering the dashboard for the tenant-admin
@app.route("/dashboardTenant/<string:tenant>")
def dashboard_tenant(tenant):
    print("Tenant: "+tenant)
    cur_date = str(datetime.datetime.now())
    cur_per = cur_date[:7]
    user = "all"

    # Request the total count and total length within the tenant for the current period
    total_count = tQueryCountPeriodTotal(tenant,cur_per)
    total_length = tQueryLengthPeriodTotal(tenant, cur_per)

    #Tenant Business Modell
    if (total_length <= 30000):
        level = "Business pro-level"
        service_charge = (total_length / 60) * (0.11)
    else:
        level = "Business ultimate-level"
        service_charge = ((30000 * (0.11/60) + (((total_length - 30000)/60)*(0.09))))
    return render_template('dashboardTenant.html', count = total_count, length = total_length, user = user, period = cur_per, level = level, charge = service_charge)


# Method to query the total amount of transcriptions within a tenant in a certain period
def tQueryCountPeriodTotal(tenant,period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    total_t_count = 0
    for file in files['Items']:
        if file['tenant'] == tenant and file['period'] == period:
            total_t_count += 1
    return total_t_count


# Method to query the total length of transcriptions within a tenant in a certain period
def tQueryLengthPeriodTotal(tenant,period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    total_length = 0
    for file in files['Items']:
        if file['tenant'] == tenant and file['period'] == period:
            file_length = int(file['length'])
            total_length += file_length
    return total_length


# Rendering the dashboard for the tenant-admin for a specific user search
@app.route("/dashboardTenant/<string:tenant>_<string:username>_<string:period>")
def dashboard_tenant_param(tenant,username,period):
    print("Tenant: "+tenant)
    print("Username: " +username)
    print("Period: " +period)
    level = "-"
    service_charge = "-"

    if(username == "" or period == ""):
        return redirect('/dashboard_tenant/'+tenant)

    # Request the total count and total length within the tenant for the current period and a certain user
    user_count = tQueryCountPeriod(tenant,username,period)
    user_length = tQueryLengthPeriod(tenant,username,period)

    return render_template('dashboardTenant.html', count = user_count, length = user_length, user = username, period = period, level = level, charge = service_charge)


# Method to query the total amount of transcriptions within a tenant in a certain period for a specific user
def tQueryCountPeriod(tenant,username,period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    cur_per = period
    total_count = 0
    for file in files['Items']:
        if file['username'] == username and file['period'] == cur_per and file['tenant'] == tenant:
            total_count += 1
    return total_count


# Method to query the total length of transcriptions within a tenant in a certain period for a specific user
def tQueryLengthPeriod(tenant,username,period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    cur_per = period
    total_length = 0
    for file in files['Items']:
        if file['username'] == username and file['period'] == cur_per and file['tenant'] == tenant:
            file_length = int(file['length'])
            total_length += file_length
    return total_length


# Rendering the dashboard for the admin and setting all variables to 0
@app.route("/dashboardAdmin")
def dashboard_admin():
    cur_per = "0"
    total_count = 0
    total_length = 0
    service_charge = 0
    level = "-"
    return render_template('dashboardAdmin.html', count=total_count, length=total_length, charge=service_charge,
                           level=level)


# Rendering the dashboard for the admin and request specific tenant information
@app.route("/dashboardAdmin/<string:tenant>_<string:period>")
def dashboard_admin_param(tenant, period):
    print("Tenant: "+tenant)
    print("Periode: "+period)

    # Query the total count, length and tenant type
    total_count = queryCountPeriod(tenant, period)
    total_length = queryLengthPeriod(tenant, period)
    tenant_type = query_tenantType(tenant)

    # Implementation of the business model
    # Business Model
    if (tenant_type == "true"):
        if (total_length <= 30000):
            level = "Business pro-level"
            service_charge = (total_length / 60) * (0.11)
        else:
            level = "Business ultimate-level"
            service_charge = ((30000 * (0.11/60)) + (((total_length - 30000) / 60) * (0.09)))
    # Private Model
    elif (tenant_type == "false"):
        if (total_length <= 60):  # free
            level = "free"
            service_charge = 0
        elif (total_length <= 660):  # pro
            level = "pro"
            service_charge = ((total_length - 60) * (0.12/60))
        else:
            level = "ultimate"
            service_charge = 600 * (0.12 / 60) + (total_length-660)*(0.09/60)
    else:
        level = "-"
        service_charge = 0

    return render_template('dashboardAdmin.html', count=total_count, length=total_length, charge=service_charge, level=level, period = period, tenant = tenant)


# Query the tenant type (single-user-tenant / multi-user-tenant) of the tenant
def query_tenantType(tenant):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    for file in files['Items']:
        if file['multi_user_tenant'] == "true" and file['tenant'] == tenant:
            return "true"
        if file['multi_user_tenant'] == "false" and file['tenant'] == tenant:
            return "false"
    return "none"


# Query the total amount of transcriptions for a tenant within a special period
def queryCountPeriod(tenant, period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    cur_per = period
    total_count = 0
    for file in files['Items']:
        if file['tenant'] == tenant and file['period'] == cur_per:
            total_count += 1
    return total_count


# Query the total length of transcriptions for a tenant within a special period
def queryLengthPeriod(tenant, period):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    cur_per = period
    total_length = 0
    for file in files['Items']:
        if file['tenant'] == tenant and file['period'] == cur_per:
            file_length = int(file['length'])
            total_length += file_length
    return total_length


# Redirect to /login
@app.route("/dashboard")
def dashboard():
    return redirect('/login')

# Rendering the welcome-page
@app.route("/welcome")
def welcome():
    return render_template('welcome.html')


# Rendering the service-page
@app.route("/serviceloggedin")
def serviceloggedin():
    return render_template('serviceloggedin.html')


# Rendering the aboutUs-page
@app.route("/aboutusloggedin")
def aboutusloggedin():
    return render_template('aboutusloggedin.html')


# Rendering the dashboard for a user
@app.route("/dashboard/<string:tenant>_<string:multiUser>_<string:username>")
def dashboard_param(tenant, multiUser, username):
    # Query of all users txt.files
    table = dynamo.Table(username)
    files = table.scan()
    files_to_display = []
    for file in files['Items']:
        if file['format'] == 'txt':
            files_to_display.append(file)

    print(files)
    print(files_to_display)

    # Query the total size, count and length of the transcriptions of the user
    date = str(datetime.datetime.now())
    cur_per = date[:7]
    total_size = querySize(username)
    total_count = queryCount(username)
    total_length = queryLength(username)

    # Calculate the costs, if the user is a single-user-tenant
    if (multiUser == "true"):
        level = "-"
        service_charge = 0
    elif (total_length <= 60):  # free
        level = "free"
        service_charge = 0
    elif (total_length <= 660):  # pro
        level = "pro"
        service_charge = ((total_length - 60) * (0.12 / 60))
    else:
        level = "ultimate"
        service_charge = (600 * (0.12 / 60) + (total_length - 660) * (0.09/60))

    return render_template('dashboard.html', tenant = tenant, multiUser = multiUser, files=files_to_display, user=username, cur_per=cur_per, count=total_count,
                           length=total_length, charge=service_charge, level=level)


# Query the total length of a user for the current period
def queryLength(username):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    date = str(datetime.datetime.now())
    cur_per = date[:7]
    files_to_display = []
    total_length = 0
    for file in files['Items']:
        if file['username'] == username and file['period'] == cur_per:
            file_length = int(file['length'])
            total_length += file_length
    return total_length


# Query the size of the transcripted files of a user for the current period
def querySize(username):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    date = str(datetime.datetime.now())
    cur_per = date[:7]
    files_to_display = []
    total_size = 0
    for file in files['Items']:
        if file['username'] == username and file['period'] == cur_per:
            file_size = int(file['size'])
            total_size += file_size
    return (total_size / 1000)


# Query the amount of the transcripted files of a user for the current period
def queryCount(username):
    table = dynamo.Table('admin-log-files')
    files = table.scan()
    date = str(datetime.datetime.now())
    cur_per = date[:7]
    files_to_display = []
    total_count = 0
    for file in files['Items']:
        if file['username'] == username and file['period'] == cur_per:
            total_count += 1
    return total_count


# Method to delete a txt.file of a user
@app.route("/delete/<string:tenant>_<string:multiUser>_<string:username>_<string:filename>")
def delete_file(username, filename, tenant, multiUser):
    table = dynamo.Table(username)
    media_format = filename[-3:]
    try:
        table.delete_item(
            Key={
                'file': filename,
                'format': media_format
            }
        )

        s3.Bucket('transcribe-bucket-bzs').delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': username + '/' + filename
                    }
                ]
            }
        )
        return redirect('/dashboard/' + tenant + "_" + multiUser + "_" + username)
    except:
        print("There was an error deleting the files")
        return "There was an error deleting the files"


# Method to download a txt.file of a user
@app.route("/download/<string:username>/<string:filename>")
def download_file(username, filename):
    table = dynamo.Table(username)
    try:
        s3.Bucket('transcribe-bucket-bzs').download_file(Key=username + '/' + filename, Filename='/tmp/' + filename)
        return send_from_directory('/tmp/', filename=filename, as_attachment=True)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print('The object does not exist')
        else:
            raise


# Creating of a unique s3 folder and dynamoDB database for a user on registration
@app.route("/createfolder", methods=["GET", "POST"])
def createfolder():
    if request.method == "POST":
        username = request.form['username']
        try:
            s3.Bucket('transcribe-bucket-bzs').put_object(Key=username + '/', Body='This is the Body')
            dynamo.create_table(TableName=username,
                                KeySchema=[
                                    {
                                        'AttributeName': 'file',
                                        'KeyType': 'HASH'  # Partition key
                                    },
                                    {
                                        'AttributeName': 'format',
                                        'KeyType': 'RANGE'  # Sort key
                                    }
                                ],
                                AttributeDefinitions=[
                                    {
                                        'AttributeName': 'file',
                                        'AttributeType': 'S'
                                    },
                                    {
                                        'AttributeName': 'format',
                                        'AttributeType': 'S'
                                    }
                                ],
                                ProvisionedThroughput={
                                    'ReadCapacityUnits': 10,
                                    'WriteCapacityUnits': 10
                                }
                                )

            print('Bucket' + username + 'has been created')
        except:
            print('There was a bucket error')
    else:
        return "This is /createfolder"
