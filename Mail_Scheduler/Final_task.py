from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

SCOPES = ['https://mail.google.com/']

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service=build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
  message = get_service().users().messages().send(userId='me', body={'raw': raw}).execute()
  print('Message Id: %s' % message['id'])
  return message
 
def main():
    sender="your_address@gmail.com"       # add the sender's email address
    to="someone1@gmail.com, someone2@gmail.com"  # add the email addresses you want to send to
    sub="Hi"                            # add subject
    message="Hello, how are you doing."  # add message content
    create_message(sender, to, sub, message)

if __name__ == '__main__':
    main()