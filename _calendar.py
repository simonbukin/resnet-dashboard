"""Retrieving Google Calendar information."""
from __future__ import print_function
import datetime
from datetime import timedelta
import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from auth.auth import calendar_id

from _redis import open_redis_connection

"""
This code is sourced from the tutorial for using the Google Calendar API
"""

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


"""
this is the end of the Google Calendar API starter code.
"""


def calendar_get_events(creds):
    """Returns a set of events from current time until end of day."""
    service = build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    UTC_OFFSET = datetime.datetime.utcnow() - datetime.datetime.now()
    # now is current time, then is midnight of today
    # time conversions to make sure the timezones are correct
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC
    then = ((datetime.datetime.now().replace(hour=0,
                                             minute=0,
                                             second=0,
                                             microsecond=0) +
             timedelta(days=1)) + UTC_OFFSET).isoformat() + 'Z'
    # get the events in the time interval from now to then
    events_result = service.events().list(calendarId=calendar_id,
                                          timeMin=now,
                                          timeMax=then,
                                          maxResults=100,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def authenticate_and_get_events():
    """Return events from calendar after authentication."""
    creds = calendar_auth_login()  # get Google Calendar credentials
    events = calendar_get_events(creds)  # get all events for today
    return events


def housecall_status(events):
    """Returns how many housecalls there are on the calendar."""
    if not events:  # no events means no housecalls
        print('No upcoming events found.')
        return 0
    count = 0
    for event in events:
        name = event['summary'].lower()
        if ('house' in name) and ('call' in name):
            count += 1  # increment # housecalls
    return count


def write_housecalls():
    """Write number of housecalls to Redis."""
    redis = open_redis_connection()
    events = authenticate_and_get_events()
    num_housecalls = housecall_status(events)
    redis.set('housecalls', num_housecalls, ex=20)


def read_housecalls():
    """Read number of housecalls from Redis."""
    redis = open_redis_connection()
    num_housecalls = redis.get('housecalls')
    return num_housecalls

calendar_auth_login()
