from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import psycopg2


conn = psycopg2.connect(database="students", user = "postgres", password = "mukesh2003", host = "127.0.0.1", port = "5432")
c = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


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

# Starting of main code part 
def main():

    a=str(input("Do you want to enter values into Student-List table(y/n):"))
    if a==('y'):
        b=int(input("Enter number of students:"))
        c.execute("CREATE TABLE IF NOT EXISTS StudentList(Name TEXT)")
        for i in range(0,b):
            name=str(input("Enter name:"))  
            c.execute( "INSERT INTO StudentList VALUES(%s)", (name,))
            conn.commit()
    else:
        print('ok') 

    # accessing the threads from mail 
    results = get_service().users().messages().list(userId='me', labelIds='INBOX').execute()
    messages = results.get('messages',[])
    inp=str(input("Do you want to enter the mail contents in table(y/n):"))
    if inp=='y':
      d=int(input("How many emails to access:"))
      values=[]
      for message in messages[0:d]:
         msg = get_service().users().messages().get(userId='me', id=message['id']).execute()
         time=int(msg['internalDate'])
         timestamp=datetime.datetime.fromtimestamp(time/1000)      # it's in epoch time so we are converting it using datetime module
         name=msg['payload']['headers']
         mailname = None
         for i in range(0,len(name)):
             if name[i]['name']=='From':                  # getting the From address of the mail from headers field
                 mailname=name[i]['value']
                 break
         cont=msg['payload']['headers']
         content = None
         for i in range(0,len(name)):
             if cont[i]['name']=='Subject':                  # getting the subject of the mail from headers field
                 content=name[i]['value']
                 break            
         values.append((str(timestamp), mailname, content))
      c.execute("CREATE TABLE IF NOT EXISTS MailList(Timestamp TIMESTAMP, Name TEXT, Content TEXT)")
      for row in values:
         print(row)
         c.execute( "INSERT INTO MailList VALUES(%s, %s, %s)", row)
         conn.commit()
    else:
        print('ok')

    c.execute("SELECT Name FROM StudentList WHERE Name NOT IN (SELECT Name FROM MailList)")
    final_result=c.fetchall()
    print("The students who have not mailed:",final_result)    
    c.close()
    conn.close()
if __name__ == '__main__':
    main()