import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel

import os
import json

credentials_json = os.getenv('GOOGLE_CREDENTIAL')
print(credentials_json)

USER_SPREADSHEET_NAME = 'UserDatabase'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
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
            raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = generate_password_hash(user.password)
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
                raise HTTPException(status_code=400, detail="Invalid credentials")

    raise HTTPException(status_code=400, detail="Invalid credentials")
