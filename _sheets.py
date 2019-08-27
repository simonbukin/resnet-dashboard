from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from _utils import json_file
from auth.auth import sheet_id

"""
Code below sourced from Google Sheets API tutorial.
"""

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TASKS_RANGE_NAME = 'Tasks!A1:J50'  # define sheet and range on sheet to get


def sheet_auth_login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('pickles/sheets_token.pickle'):
        with open('pickles/sheets_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'auth/sheets_credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('pickles/sheets_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def sheet_get_values(creds):
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=TASKS_RANGE_NAME).execute()
    values = result.get('values', [])
    return values


"""
End code sourced from Google Sheets API tutorial.
"""


def sheet_auth_json():
    """Authenticate, get sheet values, and json the resulting values."""
    creds = sheet_auth_login()  # get GSheet credentials
    values = sheet_get_values(creds)  # get the sheets values
    sheet_out = {'tasks': []}  # prepare dict for json'ing
    for value in values:  # for each row in the returned values
        # add a new dict with just the task name, description and status
        sheet_out['tasks'].append({'title': value[0],
                                   'description': value[1],
                                   'status': value[3]})
    # json the first 10 tasks, not including the header row
    json_file(sheet_out['tasks'][1:11], 'sheets.json')
