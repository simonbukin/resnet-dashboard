from __future__ import print_function
import datetime
from datetime import timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from auth.auth import calendar_id

from _utils import json_file, open_json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def calendar_auth_login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('pickles/calendar_token.pickle'):
        with open('pickles/calendar_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'auth/calendar_credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('pickles/calendar_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

""" returns a set of events from current time until end of day """
def calendar_get_events(creds):
    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    UTC_OFFSET = datetime.datetime.utcnow() - datetime.datetime.now()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    then = ((datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)) + UTC_OFFSET).isoformat() + 'Z'
    events_result = service.events().list(calendarId=calendar_id, timeMin=now, timeMax=then,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

""" returns how many housecalls there are given event json from Google Calendar API """
def housecall_status(events):
    if not events:
        print('No upcoming events found.')
    count = 0
    for event in events:
        name = event['summary'].lower();
        if ('house' in name) and ('call' in name):
            count += 1
    return count

""" """
def calendar_auth_json():
    creds = calendar_auth_login()
    events = calendar_get_events(creds)
    events_edit = {'events':[]}
    for event in events:
        new_event = {}
        params = ['id', 'created', 'summary', 'start', 'end']
        for param in params:
            new_event[param] = event[param]
        events_edit['events'].append(new_event)
    print(events_edit)
    json_file(events_edit, 'calendar.json')
