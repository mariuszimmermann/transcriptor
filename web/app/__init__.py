from flask import Flask, render_template, request, redirect, send_from_directory
import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
from npm.bindings import npm_install
import boto3
import botocore
import os

app = Flask(__name__)

# Setting the credentials
aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

# Setting the AWS S3 and DynamoDB
s3 = boto3.resource('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)
dynamo = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)

#jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))

npm_install('app/pem')

# AWS Cognito Access-token
def is_token_valid(token):
    pems_dict = {
        'kid1': 'pem1',
        'kid2': 'pem2'
    }

    kid = jwt.get_unverified_header(token)['kid']
    pem = pems_dict.get(kid, None)

    if pem is None:
        print ('kid false')
        return False

    try:
        decoded_token = jwt.decode(token, pem, algorithms=['RS256'])
        iss = 'https://cognito-idp.eu-central-1.amazonaws.com/'+user_pool_id
        if decoded_token['iss'] != iss:
            print ('iss false')
            return False
        elif decoded_token['token_use'] != 'access':
            print ('access false')
            return False
        return True
    except Exception:
        return False

# Rendering validate.html
@app.route("/validate")
def validate():
    return render_template('validate.html')


# Rendering services.html
@app.route("/services")
def services():
    return render_template('services.html')


# Rendering aboutUS.html
@app.route("/aboutUs")
def aboutUs():
    return render_template('aboutUs.html')


# Rendering the index.html
@app.route("/")
def index():
    return render_template('index.html')


# Rendering the logIn.html
@app.route("/login")
def login():
    return render_template('logIn.html')


# Rendering the register.html / incl. POST GET
@app.route("/register", methods = ['POST', 'GET'])
def register():
    return render_template('register.html')


# Rendering the registerNewT.html
@app.route("/registernewt", methods=['POST', 'GET'])
def registernewt():
        return render_template('registerNewT.html')


# POST Method for protected API
@app.route("/api/protected_api", methods=["POST"])
def protected_api():
    access_token = request.form['access_token']
    if (is_token_valid(access_token)):
        print('some protected data from api')
    else:
        print('bad token', 401)



