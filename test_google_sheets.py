import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEETS_CREDENTIALS, USER_SPREADSHEET_NAME, TASK_SPREADSHEET_NAME

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)

# Test user sheet
try:
    user_sheet = client.open(USER_SPREADSHEET_NAME).sheet1
    print(f"Connected to User Google Sheets: {USER_SPREADSHEET_NAME}")
except gspread.SpreadsheetNotFound:
    print(f"User Spreadsheet '{USER_SPREADSHEET_NAME}' not found.")
except Exception as e:
    print(f"Failed to connect to User Google Sheets: {e}")

# Test task sheet
try:
    task_sheet = client.open(TASK_SPREADSHEET_NAME).sheet1
    print(f"Connected to Task Google Sheets: {TASK_SPREADSHEET_NAME}")
except gspread.SpreadsheetNotFound:
    print(f"Task Spreadsheet '{TASK_SPREADSHEET_NAME}' not found.")
except Exception as e:
    print(f"Failed to connect to Task Google Sheets: {e}")
