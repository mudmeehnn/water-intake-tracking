import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from config import GOOGLE_SHEETS_CREDENTIALS, TASK_SPREADSHEET_NAME

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)
intake_sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

water_intake_router = APIRouter()

class OldIntakeLog(BaseModel):
    date: datetime
    amount_cups: float
    daily_goal: float

class NewIntakeLog(BaseModel):
    date: datetime

class Goal(BaseModel):
    date: datetime
    daily_goal_cups: float

# Helper functions
def get_all_logs(sheet):
    return sheet.get_all_records()

def add_log_to_sheet_with_amount(sheet, log):
    rows = sheet.get_all_records()
    for i, row in enumerate(rows, start=2):  # starting from row 2 to skip headers
        if row['date'] == log.date.strftime("%Y-%m-%d"):
            # Update the amount_cups by incrementing the existing value
            existing_amount = float(row['amount_cups'])
            new_amount = existing_amount + log.amount_cups
            sheet.update_cell(i, 2, new_amount)
            return
    # If no matching date found, append new row with the given amount
    sheet.append_row([log.date.strftime("%Y-%m-%d"), log.amount_cups, ''])

def add_log_to_sheet_increment(sheet, log):
    rows = sheet.get_all_records()
    for i, row in enumerate(rows, start=2):  # starting from row 2 to skip headers
        if row['date'] == log.date.strftime("%Y-%m-%d"):
            # Increment the existing amount_cups by 1
            existing_amount = float(row['amount_cups'])
            new_amount = existing_amount + 1
            sheet.update_cell(i, 2, new_amount)
            return
    # If no matching date found, append new row with amount_cups as 1
    sheet.append_row([log.date.strftime("%Y-%m-%d"), 1, ''])

def update_goal_in_sheet(sheet, goal):
    rows = sheet.get_all_records()
    for i, row in enumerate(rows, start=2):  # starting from row 2 to skip headers
        if row['date'] == goal.date.strftime("%Y-%m-%d"):
            # Update the daily_goal_cups
            sheet.update_cell(i, 3, goal.daily_goal_cups)
            return
    # If no matching date found, append new row with amount_cups as 0
    sheet.append_row([goal.date.strftime("%Y-%m-%d"), 0, goal.daily_goal_cups])

def get_logs_by_date_range(sheet, start_date, end_date):
    logs = get_all_logs(sheet)
    filtered_logs = [log for log in logs if start_date <= datetime.strptime(log['date'], "%Y-%m-%d") <= end_date]
    return filtered_logs

# Endpoints
@water_intake_router.post("/log_with_amount", response_model=OldIntakeLog)
def log_intake_with_amount(log: OldIntakeLog):
    add_log_to_sheet_with_amount(intake_sheet, log)
    return log

@water_intake_router.post("/log", response_model=NewIntakeLog)
def log_intake(log: NewIntakeLog):
    add_log_to_sheet_increment(intake_sheet, log)
    return log

@water_intake_router.get("/logs", response_model=List[OldIntakeLog])
def get_logs():
    logs = get_all_logs(intake_sheet)
    return logs

@water_intake_router.get("/logs/daily", response_model=List[OldIntakeLog])
def get_daily_logs(date: datetime):
    logs = get_logs_by_date_range(intake_sheet, date, date)
    return logs

@water_intake_router.get("/logs/weekly", response_model=List[OldIntakeLog])
def get_weekly_logs(date: datetime):
    start_date = date - timedelta(days=date.weekday())  # Monday of the current week
    end_date = start_date + timedelta(days=6)  # Sunday of the current week
    logs = get_logs_by_date_range(intake_sheet, start_date, end_date)
    return [OldIntakeLog(date=datetime.strptime(log['date'], "%Y-%m-%d"),
                      amount_cups=float(log['amount_cups']),
                      daily_goal=float(log['daily_goal']))
            for log in logs]

@water_intake_router.get("/logs/monthly", response_model=List[OldIntakeLog])
def get_monthly_logs(date: datetime):
    start_date = date.replace(day=1)  # First day of the current month
    next_month = start_date.replace(month=start_date.month % 12 + 1, day=1)
    end_date = next_month - timedelta(days=1)  # Last day of the current month
    logs = get_logs_by_date_range(intake_sheet, start_date, end_date)
    return [OldIntakeLog(date=datetime.strptime(log['date'], "%Y-%m-%d"),
                      amount_cups=float(log['amount_cups']),
                      daily_goal=float(log['daily_goal']))
            for log in logs]

@water_intake_router.get("/progress")
def get_progress(date: datetime):
    daily_logs = get_logs_by_date_range(intake_sheet, date, date)
    total_intake = sum(float(log['amount_cups']) for log in daily_logs)
    
    # Find the row for the specified date
    rows = intake_sheet.get_all_records()
    daily_goal = 0  # Default goal
    for row in rows:
        if row['date'] == date.strftime("%Y-%m-%d"):
            daily_goal = float(row['daily_goal'])
            break

    progress = (total_intake / daily_goal) * 100 if daily_goal else 0

    return {"date": date, "total_intake_cups": total_intake, "daily_goal_cups": daily_goal, "progress": progress}

@water_intake_router.post("/goal", response_model=Goal)
def set_daily_goal(goal: Goal):
    # Retrieve the previous day's goal from the sheet
    previous_goal = intake_sheet.cell(1, 3).value
    if not previous_goal:
        previous_goal = 8  # Default to 8 cups if there is no previous goal

    # Update the daily goal in the sheet
    update_goal_in_sheet(intake_sheet, goal)

    return goal

@water_intake_router.put("/goal", response_model=Goal)
def update_daily_goal(goal: Goal):
    # Update the daily goal in the sheet (for simplicity, assuming it's in the first row, third column)
    update_goal_in_sheet(intake_sheet, goal)
    return goal
