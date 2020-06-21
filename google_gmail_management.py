#!/usr/bin/env python
# -*- coding: utf-8 -*-

#pip install --upgrade google-api-python-client

from __future__ import print_function
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from email.mime.text import MIMEText
import base64
from google.oauth2 import service_account


# Use creds to create a client to interact with the Google Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
#SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
#SERVICE_ACCOUNT_FILE = 'service-key.json'
SERVICE_ACCOUNT_FILE = 'Pbpython-key.json'
# Account email
EMAIL_FROM = 'oscarsaeztrujillo@gmail.com'

# Call the Gmail API
def con_google_gmail(SCOPES, SERVICE_ACCOUNT_FILE, EMAIL_FROM):
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(EMAIL_FROM)
    service = build('gmail', 'v1', credentials=delegated_credentials)
    return service

# Creamos el e-mail
def create_email(to, subject, message_text):
    sender = EMAIL_FROM
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    #return {'raw': base64.urlsafe_b64encode(message.as_string())}
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

# Enviamos el e-mail
def send_email(to, subject, message_text):
    user_id = 'me'
    service = con_google_gmail(SCOPES, SERVICE_ACCOUNT_FILE, EMAIL_FROM)
    message = create_email(to, subject, message_text)
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
