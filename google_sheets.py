import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEETS_CREDENTIALS, TASK_SPREADSHEET_NAME
from tasks import Task

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)

sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

def sync_tasks_to_sheets():
    sheet.clear()
    sheet.append_row(['ID', 'Title', 'Description', 'Completed'])
    for task in Task:
        sheet.append_row([task['id'], task['title'], task['description'], task['completed']])
