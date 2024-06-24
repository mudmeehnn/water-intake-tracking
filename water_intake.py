import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime, timedelta

from config import GOOGLE_SHEETS_CREDENTIALS, TASK_SPREADSHEET_NAME

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)
intake_sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

water_intake_router = APIRouter()

class IntakeLog(BaseModel):
    date: datetime
    amount: float

class Goal(BaseModel):
    daily_goal: float

def get_all_logs():
    return intake_sheet.get_all_records()

def add_log_to_sheet(log):
    intake_sheet.append_row([log.date.strftime("%Y-%m-%d"), log.amount])

def get_logs_by_date_range(start_date, end_date):
    logs = get_all_logs()
    filtered_logs = [log for log in logs if start_date <= datetime.strptime(log['date'], "%Y-%m-%d") <= end_date]
    return filtered_logs

@water_intake_router.post("/log", response_model=IntakeLog)
def log_intake(log: IntakeLog):
    add_log_to_sheet(log)
    return log

@water_intake_router.get("/logs", response_model=List[IntakeLog])
def get_logs():
    logs = get_all_logs()
    return logs

@water_intake_router.get("/logs/daily", response_model=List[IntakeLog])
def get_daily_logs(date: datetime):
    logs = get_logs_by_date_range(date, date)
    return logs

@water_intake_router.get("/logs/weekly", response_model=List[IntakeLog])
def get_weekly_logs(date: datetime):
    start_date = date - timedelta(days=date.weekday())  # Monday of the current week
    end_date = start_date + timedelta(days=6)  # Sunday of the current week
    logs = get_logs_by_date_range(start_date, end_date)
    return logs

@water_intake_router.get("/logs/monthly", response_model=List[IntakeLog])
def get_monthly_logs(date: datetime):
    start_date = date.replace(day=1)  # First day of the current month
    next_month = start_date.replace(month=start_date.month % 12 + 1, day=1)
    end_date = next_month - timedelta(days=1)  # Last day of the current month
    logs = get_logs_by_date_range(start_date, end_date)
    return logs

@water_intake_router.get("/progress")
def get_progress(date: datetime):
    daily_logs = get_logs_by_date_range(date, date)
    total_intake = sum(float(log['amount']) for log in daily_logs)
    # Retrieve the daily goal from the sheet (for simplicity, assuming it's in the first row, third column)
    daily_goal = float(intake_sheet.cell(1, 3).value)

    progress = (total_intake / daily_goal) * 100 if daily_goal else 0

    return {"date": date, "total_intake": total_intake, "daily_goal": daily_goal, "progress": progress}

@water_intake_router.post("/goal", response_model=Goal)
def set_daily_goal(goal: Goal):
    # Update the daily goal in the sheet (for simplicity, assuming it's in the first row, third column)
    intake_sheet.update_cell(1, 3, goal.daily_goal)
    return goal

@water_intake_router.put("/goal", response_model=Goal)
def update_daily_goal(goal: Goal):
    intake_sheet.update_cell(1, 3, goal.daily_goal)
    return goal