import botocore as botocore
from flask import Flask, render_template, redirect, request
import boto3
import os
import time
import json
from npm.bindings import npm_install
from random import randint
import requests
import datetime
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.aac import AAC
from mutagen.flac import FLAC


app = Flask(__name__)

#AWS keys from environment
aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

#Setting up s3, db and transcribe api
s3 = boto3.resource('s3', aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access_key)
dynamo = boto3.resource('dynamodb', region_name='us-east-2', aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access_key)
transcribe = boto3.client('transcribe', region_name='us-east-2', aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_access_key)

npm_install('app/pem')

#Route for transcription
@app.route("/transcribe/<string:username>/<string:filename>")
def transcribe_start(username, filename):
    media_format = filename[-3:]  # This gets the format of the audio file, e.g. mp3

    #Uploaded audio file is saved here
    audio_file_uri = "https://transcribe-bucket-bzs.s3.us-east-2.amazonaws.com/" + username + "/" + filename
    table = dynamo.Table(username)

    # Define a job name and lets go
    job_id = str(randint(0,100000))
    job_name = filename
    print('Media format: ' + media_format)

    #Start the transcription job
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': audio_file_uri},
        OutputBucketName='transcribe-bucket-bzs',
        LanguageCode='de-DE'
    )
    print('The transcription has been started')

    url = 'http://localhost/transcribehandler/' + username + '/' + filename + '/' + job_name

    time.sleep(10)

    response = render_loadingpage()
    return redirect('/transcribehandler/' + username + '/' + filename + '/' + job_name)

#Route for the actual transcription in the backend
@app.route("/transcribehandler/<string:username>/<string:filename>/<string:jobname>", methods=['POST', 'GET'])
def transcribe_organizer(username, filename, jobname):

        response = render_loadingpage()
        #Loop to print debugging info for while the transcription
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=jobname)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet...")
            time.sleep(5)
        print("Transcription has been completed")
        time.sleep(10)

        #Download the transcription .json file from S3
        try:
            s3.Bucket('transcribe-bucket-bzs').download_file(Key=filename + '.json', Filename='/tmp/' + filename + '.json') #/tmp/audio.mp3.json
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                print('The object does not exist')
            else:
                raise
        filepath = '/tmp/' + filename + '.json'
        filename_no_type = filename[:len(filename)-4]

        #Loading the json file into the script
        with open(filepath) as json_file:
            data = json.load(json_file)
            content = data['results']['transcripts'][0]['transcript']

        #Now write the transcription into the .txt file
        with open('/tmp/' + filename_no_type + ".txt", "w") as file:
            file.write(content)

        #Upload the completed .txt file to the dashboard of the user
        s3.Bucket('transcribe-bucket-bzs').upload_file('/tmp/' + filename_no_type + '.txt', username + '/' + filename_no_type + '.txt')
        table = dynamo.Table(username)
        table.put_item(
            Item={
                'file': filename_no_type + '.txt',
                'format': 'txt',
            }
        )

        #Remove all traces of the audio file to save space on S3
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
        except:
            print("There was an error deleting the audio files")
        return redirect('/transrun')

#Route for starting the transcription
@app.route("/trans/<string:tenant>_<string:multiUser>_<string:username>", methods =['GET', 'POST'])
def trans(tenant,multiUser,username):
    if request.method == 'POST':
        table = dynamo.Table(username)
        tableLog = dynamo.Table('admin-log-files')
        filename = request.files['files'].filename
        media_format = filename[-3:]
        multi_user_tenant = multiUser


        # Media_format check
        if media_format != "mp3":
            if media_format != "mp4":
                if media_format != "aac":
                    if media_format != "lac":
                        return render_template('trans.html', user=username)

        cur_time = str(datetime.datetime.now())
        cur_period = cur_time[:7]
        id = username + cur_time

        #Upload the audio file to S3
        s3.Bucket('transcribe-bucket-bzs').put_object(Key=username + '/' + filename, Body=request.files['files'])

        # Getting s3 file and read duration
        file = request.files['files']

        if (media_format == 'mp3'):
            audio = MP3(file)
        if (media_format == 'mp4'):
            audio = MP4(file)
        if (media_format == 'aac'):
            audio = AAC(file)
        if (media_format == 'lac'):
            audio = FLAC(file)

        length = int(audio.info.length)
        print("+++ Length: "+str(length))

        #Save the size of the audio file
        size = str(boto3.resource('s3').Bucket('transcribe-bucket-bzs').Object(username + '/' + filename).content_length)
        print("+++Size: " + size)

        #Create the log for the billing and tenant information
        try:
            tableLog.put_item(
                Item={
                    'id': id,
                    'fileformat': media_format,
                    'size': int(size),
                    'period': cur_period,
                    'time': cur_time,
                    'username': username,
                    'length': length,
                    'tenant': tenant,
                    'multi_user_tenant': multi_user_tenant
                }
            )
            print("Log-files successfully uploaded!")
        except:
            print("There was an issue uploading the log-files!")

        try:
            table.put_item(
                Item={
                    'file': filename,
                    'format': media_format
                }
            )
            return redirect('/transcribe/' + username + '/' + filename)
        except:
            return 'There was an issue adding your task'
    else:
        return render_template('trans.html', user=username, multiUser = multiUser, tenant = tenant)

#Route for transcription complete page
@app.route("/transrun")
def transrun():
    return render_template('transRun.html')


def render_loadingpage():
    return render_template('transcribe.html')





