# config.py
import os
import json

credentials_json = os.getenv('GOOGLE_CREDENTIALS')
GOOGLE_SHEETS_CREDENTIALS = json.loads(credentials_json)

# GOOGLE_SHEETS_CREDENTIALS = 'credentials.json'
USER_SPREADSHEET_NAME = 'UserDatabase'
TASK_SPREADSHEET_NAME = 'TasksDatabase'
