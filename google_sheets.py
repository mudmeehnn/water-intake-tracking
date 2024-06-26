import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEETS_CREDENTIALS, TASK_SPREADSHEET_NAME
from water_intake import OldIntakeLog, NewIntakeLog

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)

sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

def sync_intake_logs_to_sheets():
    sheet.clear()
    sheet.append_row(['Date', 'Amount', 'Daily Goal'])
    previous_goal = None
    
    for log in OldIntakeLog:
        if log['daily_goal']:
            previous_goal = log['daily_goal']
        
        sheet.append_row([log['date'].strftime("%Y-%m-%d"), log['amount_cups'], log.get('daily_goal') or previous_goal])

    for log in NewIntakeLog:
        if log['daily_goal']:
            previous_goal = log['daily_goal']
        
        sheet.append_row([log['date'].strftime("%Y-%m-%d"), log['amount_cups'], log.get('daily_goal') or previous_goal])
