import boto3
import json
import os

def get_session_file():
    session = {}
    session_file_retrieved = False

    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(
            Bucket=os.environ.get('S3_BUCKET'),
            Key=os.environ.get('S3_SESSION_FILE_KEY')
        )
        session_json = response['Body'].read().decode('utf-8')
        session = json.loads(session_json)
        session_file_retrieved = True

    except Exception as e:
        session_file_retrieved = False

    return session if session_file_retrieved else None