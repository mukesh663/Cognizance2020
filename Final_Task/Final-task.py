from __future__ import print_function
from logging import logMultiprocessing
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime, itertools


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/spreadsheets']


def main():
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

    gmailservice=build('gmail', 'v1', credentials=creds)
    sheetservice=build('sheets', 'v4', credentials=creds)
    
    # Starting of main code part 
    a=str(input(print("Do you want to create a new spreadsheet(y/n):")))

    if a == ('y'):
        spreadsheet = {'properties': {'title': 'Student_list'}}   #you can also give your own name for sheet
        spreadsheet = sheetservice.spreadsheets().create(body=spreadsheet,fields='spreadsheetId').execute()
        SPREADSHEET_ID1 = spreadsheet.get('spreadsheetId')
    else:
        SPREADSHEET_ID1 = input("Enter the spreadsheet Id:")
    
    b=str(input("Do you want to enter names in spreadsheet (y/n):"))
    if b==('y'):
        values = [['Name']] 
        c=int(input("enter number of students:"))
        for i in range(0,c):
            d=str(input("Enter name:"))
            values.append([d])
        print(values)
        body = {'values': values }    # to update spreadsheet using python code
        result = sheetservice.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID1, range='A1:A',valueInputOption='RAW', body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
    else:
        print("ok")
    
    # accessing the threads from mail and storing it in spread sheet
    results = gmailservice.users().messages().list(userId='me', labelIds='INBOX').execute()
    messages = results.get('messages',[])
    e=int(input("How many emails to access:"))
    
    values2=[['Name','Timestamp','Content']]    
    for message in messages[0:e]:
     msg = gmailservice.users().messages().get(userId='me', id=message['id']).execute()
     time=int(msg['internalDate'])
     timestamp=datetime.datetime.fromtimestamp(time/1000)      # it's in epoch time so we are converting it using datetime module
     name=msg['payload']['headers']
     for i in range(0,len(name)):
        if name[i]['name']=='From':                  # getting the From address of the mail from headers field
            mailname=name[i]['value']
            break
     content=msg['snippet']                           # subject of the mail can also be found but it makes the program slow
     values2.append([mailname,str(timestamp),content])
    
    f=str(input("Do you want to create a new spreadsheet for storing mail content(y/n):"))
    if f==('y'):
      spreadsheet = {'properties': {'title': 'Mail_list'}}
      spreadsheet = sheetservice.spreadsheets().create(body=spreadsheet,fields='spreadsheetId').execute()
      SPREADSHEET_ID2 = spreadsheet.get('spreadsheetId')
    else:
        SPREADSHEET_ID2=input("Enter spreadsheet Id:")

    body2 = {'values': values2 } 
    result2 = sheetservice.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID2, range='A1:C',valueInputOption='RAW', body=body2).execute()
    print('{0} cells updated.'.format(result2.get('updatedCells')))

    compare1 = sheetservice.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID1, range='A2:A').execute()
    compare2 = sheetservice.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID2, range='A2:A').execute()
    
    # the values of compare1 and 2 are stored as list inside another list(nested list), so we are extracting it using itertools module
    final_result= set(itertools.chain(*compare1['values']))-set(itertools.chain(*compare2['values']))   
    print("The students who have not mailed:",final_result)    # set data type is used for omitting duplicate entries

if __name__ == '__main__':
    main()
