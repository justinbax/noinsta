import json
from instagrapi.types import DirectMessage, DirectThread
import os
from datetime import datetime, timedelta, timezone
from time import mktime
from typing import List

from get_session_file import get_session_file
from login_and_get_message import login_and_get_messages
from send_email import send_email

def parse_messages(messages: List[DirectMessage], thread: DirectThread):
    parsed_messages = []
    messages.sort(key=lambda m: mktime(m.timestamp.timetuple()))

    for m in messages:
        sent_by = [user.full_name for user in thread.users if user.pk == m.user_id]
        sent_by = sent_by[0] if len(sent_by) > 0 else '???'
        if m.text:
            parsed_messages.append({
                'sent_by': sent_by,
                'text': m.text,
                'time': int(mktime(m.timestamp.timetuple())),
            })

    return parsed_messages

def lambda_handler(event, context):

    session = get_session_file()
    threads = login_and_get_messages(session)

    if not threads:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Something went wrong while logging in to Instagram API",
            }),
        }
    
    recent_messages_threshold_minutes = int(os.environ.get('RECENT_MESSAGES_THRESHOLD_MINUTES'))
    
    cleaned_up_threads = []
    for thread in threads:
        cleaned_up_threads.append({
            'title': thread.thread_title,
            'messages': parse_messages([
                message for message in thread.messages
                if message.timestamp > (
                    datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=recent_messages_threshold_minutes)
                ) and not message.is_sent_by_viewer
            ], thread),
        })

    cleaned_up_threads = [thread for thread in cleaned_up_threads if len(thread['messages']) > 0]

    if len(cleaned_up_threads) > 0:
        print('Got messages, sending email...')
        send_email(cleaned_up_threads)

    return {
        "statusCode": 200,
        "body": json.dumps(cleaned_up_threads),
    }
