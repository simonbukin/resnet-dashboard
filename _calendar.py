from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from auth.auth import calendar_id

from _utils import pickle_file, open_pickle

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

def calendar_get_events(creds):
    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
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
            # ind = None
            # try:
            #     ind = name.index('inc')
            # except ValueError:
            #     print('No ticket number in calendar event')
            # print(name[:ind], name[ind:ind+10])
    return count

""" """
def calendar_auth_pickle():
    creds = calendar_auth_login()
    events = calendar_get_events(creds)
    pickle_file(events, 'calendar.pickle')
