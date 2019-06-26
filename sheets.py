from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from utils import pickle_file, open_pickle

sheet_id = '1gazwxvAyqbV2bjm11h0PHrkocBzvpvU1RlmQfRSLb1A'

""" Code sourced from Google Sheets API tutorial """

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TASKS_RANGE_NAME = 'Tasks!A1:J50'

def auth_login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('pickles/token.pickle'):
        with open('pickles/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'auth/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('pickles/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_sheet_values(creds):
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=TASKS_RANGE_NAME).execute()
    values = result.get('values', [])
    return values

""" end code sourced from Google Sheets API tutorial """

""" authenticate, get sheet values, and pickle the resulting values """
def auth_get_pickle():
    creds = auth_login()
    values = get_sheet_values(creds)
    pickle_file(values[:11], 'sheets.pickle')
