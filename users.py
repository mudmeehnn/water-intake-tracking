import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration file for storing sensitive information like Google Sheets credentials path
GOOGLE_SHEETS_CREDENTIALS = 'path/to/credentials.json'
USER_SPREADSHEET_NAME = 'UserDatabase'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)
user_sheet = client.open(USER_SPREADSHEET_NAME).sheet1

users_router = APIRouter()

class User(BaseModel):
    username: str
    password: str

def get_all_users():
    return user_sheet.get_all_records()

def add_user_to_sheet(username, password):
    user_sheet.append_row([username, password])

@users_router.post("/register")
def register(user: User):
    users = get_all_users()
    for u in users:
        if u['username'] == user.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password = generate_password_hash(user.password, method='sha256')
    add_user_to_sheet(user.username, hashed_password)

    return {"message": "User registered successfully"}

@users_router.post("/login")
def login(user: User):
    users = get_all_users()
    for u in users:
        if u['username'] == user.username:
            stored_password = u['password']
            if check_password_hash(stored_password, user.password):
                return {"message": "Login successful"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
