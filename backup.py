import os.path
import datetime as dt

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
        # Build the Google Calendar API service
        service = build('calendar', 'v3', credentials=creds)

        # Define the event details
        event = {
            'summary': 'My Python Event',
            'location': 'Somewhere Online',
            'description': 'Some details',
            'start': {
                'dateTime': '2024-05-21T09:00:00+03:00',
                'timeZone': 'Africa/Nairobi',
            },
            'end': {
                'dateTime': '2024-05-21T17:00:00+03:00',
                'timeZone': 'Africa/Nairobi',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=2'
            ],
            'attendees': [
                {'email': 'example@gmail.com'},
                {'email': 'someemail@gmail.com'},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # Insert the event and get the event ID
        event = service.events().insert(calendarId='primary', body=event).execute()
        event_id = event.get('id')

        # Print the event link and event ID
        print('Event created: %s' % (event.get('htmlLink')))
        print('Event ID: %s' % event_id)  # This line prints the event ID

        # Ask the user if they want to update the event
        update_choice = input('Do you want to update an event? (yes/no): ').strip().lower()
        if update_choice == 'yes':
            update_event_id = input('Enter the event ID to update: ').strip()
            updated_event = {
                'summary': 'Updated Python Event',
                'location': 'New Location',
                'description': 'Updated details',
                'start': {
                    'dateTime': '2024-05-22T10:00:00+03:00',
                    'timeZone': 'Africa/Nairobi',
                },
                'end': {
                    'dateTime': '2024-05-22T18:00:00+03:00',
                    'timeZone': 'Africa/Nairobi',
                },
            }
            patch_event(service, 'primary', update_event_id, updated_event)

        # Ask the user if they want to delete the event
        delete_choice = input('Do you want to delete an event? (yes/no): ').strip().lower()
        if delete_choice == 'yes':
            delete_event_id = input('Enter the event ID to delete: ').strip()
            delete_event(service, 'primary', delete_event_id)

    except HttpError as error:
        print('An error occurred:', error)


def patch_event(service, calendar_id, event_id, updated_event):
    try:
        event = service.events().patch(calendarId=calendar_id, eventId=event_id, body=updated_event).execute()
        print('Event updated: %s' % (event.get('htmlLink')))
    except HttpError as error:
        print('An error occurred:', error)


def delete_event(service, calendar_id, event_id):
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print('Event deleted')
    except HttpError as error:
        print('An error occurred:', error)


if __name__ == '__main__':
    main()
