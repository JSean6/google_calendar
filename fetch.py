import os.path
import datetime as dt
import sqlite3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None

    # Check if token.json exists to get the credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        event_result = service.events().list(calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime").execute()
        events = event_result.get("items", [])

        if not events:
            print("No upcoming events")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            con = sqlite3.connect('events.db')
            cur = con.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS tablename (
                    id INTEGER PRIMARY KEY,
                    time TIME,
                    title TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            con.commit()
            con.close()
            def save_to_database(time, title):
                con = sqlite3.connect('events.db')
                cur = con.cursor()
                cur.execute('INSERT INTO downloaded_urls (url, title) VALUES (?, ?)', (time, title))
                con.commit()
                con.close()
                save_to_database(time, title)

    except HttpError as error:
        print("An error occurred:", error)



if __name__ == '__main__':
    main()