import smtplib
import ssl
from email.mime.text import MIMEText
from typing import Dict
import os

def format_message(message: Dict):
    name_split = message['sent_by'].split(' ')
    short_name = name_split[0]
    if len(name_split) > 1:
        short_name += f' {name_split[1][0]}.'

    short_message = (message['text'][:37] + '...') if len(message['text']) > 40 else message['text']
    return f'{short_name}: {short_message}\n'

def send_email(threads: Dict):
    context = ssl.create_default_context()
    smtp = smtplib.SMTP(os.environ.get('EMAIL_SERVER'), int(os.environ.get('EMAIL_PORT')))

    smtp.ehlo()
    smtp.starttls(context=context)
    smtp.ehlo()

    from_addr = os.environ.get('EMAIL_ADDRESS')
    to_addr = os.environ.get('EMAIL_TO')

    text = '\n'
    for thread in threads[:3]:
        text += f'From {thread['title']}:\n'
        for m in thread['messages'][:10]:
            text += format_message(m)
        if len(thread['messages']) > 10:
            text += f'and {len(thread['messages']) - 10} others.'
        text += '\n'

    if len(threads) > 3:
        text += f'and {len(threads) - 3} other conversations.'

    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = to_addr

    smtp.login(from_addr, os.environ.get('EMAIL_PASSWORD'))
    smtp.sendmail(msg['From'], to_addr, msg.as_string())