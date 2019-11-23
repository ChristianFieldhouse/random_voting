import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import string


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def sheet_editor():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print("doing some hella cool stuff")
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet.values()
    
SHEET_EDITTOR = sheet_editor()
def restart():
    SHEET_EDITTOR = sheet_editor()
    return 0
    
def write_row(sheet_id="", values=[], row_index=0):
    range=f'A{row_index}:{string.ascii_uppercase[len(values)+1]}{row_index}'
    body ={
          "majorDimension": "ROWS",
          "values": [values],
          "range": range,
    }

    return SHEET_EDITTOR.update(
        spreadsheetId=sheet_id,
        range=range,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    
def get_range(sheet_id="", range=""):
    result = SHEET_EDITTOR.get(spreadsheetId=sheet_id,
                                range=range).execute()
    return result.get('values', [])
