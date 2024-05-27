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

        # Define the event details through user input
        event = get_event_details()
        if not event:
            return

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
            updated_event = get_event_details(update=True)
            if updated_event:
                patch_event(service, 'primary', update_event_id, updated_event)

        # Ask the user if they want to delete the event
        delete_choice = input('Do you want to delete an event? (yes/no): ').strip().lower()
        if delete_choice == 'yes':
            delete_event_id = input('Enter the event ID to delete: ').strip()
            delete_event(service, 'primary', delete_event_id)

    except HttpError as error:
        print('An error occurred:', error)


def get_event_details(update=False):
    def get_input(prompt, required_format=None):
        while True:
            value = input(prompt)
            if required_format:
                try:
                    dt.datetime.strptime(value, required_format)
                except ValueError:
                    print(f"Invalid format. Please use the format: {required_format}")
                    continue
            return value

    summary = input("Enter the event summary [i.e event name]: ").strip()
    location = input("Enter the event location: ").strip()
    description = input("Enter the event description: ").strip()

    start_datetime = get_input("Enter the start date and time (YYYY-MM-DDTHH:MM:SS+HH:MM): ", "%Y-%m-%dT%H:%M:%S%z")
    end_datetime = get_input("Enter the end date and time (YYYY-MM-DDTHH:MM:SS+HH:MM): ", "%Y-%m-%dT%H:%M:%S%z")

    time_zone = input("Enter the time zone (e.g., Africa/Nairobi): ").strip()
    recurrence = input("Enter the recurrence rule (e.g., RRULE:FREQ=DAILY;COUNT=2): ").strip()

    attendees = []
    while True:
        attendee_email = input("Enter attendee email (or 'done' to finish): ").strip()
        if attendee_email.lower() == 'done':
            break
        attendees.append({'email': attendee_email})

    reminders = {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
    }

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': time_zone,
        },
        'recurrence': [recurrence],
        'attendees': attendees,
        'reminders': reminders,
    }

    return event


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
