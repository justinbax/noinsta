from instagrapi import Client
from instagrapi.types import DirectThread
from instagrapi.exceptions import LoginRequired
from typing import List, Dict
import boto3
import os
import json

def write_new_session(client: Client):
    client.dump_settings('/tmp/session.json')
    settings_json = json.dumps(client.get_settings())
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Body=settings_json.encode('utf-8'),
        Bucket=os.environ.get('S3_BUCKET'),
        Key=os.environ.get('S3_SESSION_FILE_KEY')
    )

def get_messages(client: Client) -> List[DirectThread]:
    threads = client.direct_threads(selected_filter='unread')
    return threads

def login_and_get_messages(session: Dict | None) -> List[DirectThread] | None:
    cl = Client()

    login_via_session = False
    login_via_pw = False

    USERNAME = os.environ.get('INSTAGRAM_USERNAME')
    PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')

    if session:
        try:
            cl.set_settings(session)
            cl.login(USERNAME, PASSWORD)

            # Check if session is valid
            try:
                threads = get_messages(cl)
                print('Connected with session.')
                return threads

            except LoginRequired:
                print('Session is invalid, need to login via username and password')
                old_session = cl.get_settings()

                # Use the same device UUIDs across logins
                cl.set_settings({})
                cl.set_uuids(old_session['uuids'])

                cl.login(USERNAME, PASSWORD)

            login_via_session = True
            print('Logged in via session!')
        except Exception as e:
            print('Could not login user using session information: %s' % e)

    if not login_via_session:
        try:
            print('Attempting to login via username and password. username: %s' % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                print('Succeeded!')
                login_via_pw = True
            else:
                print('Failed!')
        except Exception as e:
            print('Could not login user using username and password: %s' % e)

    if not login_via_pw and not login_via_session:
        print('Both login attempts failed.')
        return None
    
    try:
        print('Writing the new session to S3...')
        write_new_session(cl)
        print('done.')
        threads = get_messages(cl)
        return threads
    except Exception as e:
        print('Error at the very end: %s' % e)
        return None
