from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

sheet_id = '1gazwxvAyqbV2bjm11h0PHrkocBzvpvU1RlmQfRSLb1A'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TASKS_RANGE_NAME = 'Tasks!A1:J50'

def auth_login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
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

def pickle_values(values):
    with open('data.pickle', 'wb') as data:
        pickle.dump(values, data)

def auth_get_pickle():
    creds = auth_login()
    values = get_sheet_values(creds)
    pickle_values(values)

# class Task:
#     def __init__(self, task, desc, techs, stat, create, finish, due):
#         self.task = task
#         self.desc = desc
#         self.techs = techs
#         self.status = stat
#         self.created = create
#         self.finished = finish
#         self.due = due
