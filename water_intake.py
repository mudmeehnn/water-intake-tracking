import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta, date

from config import GOOGLE_SHEETS_CREDENTIALS, TASK_SPREADSHEET_NAME

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)
intake_sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

water_intake_router = APIRouter()

class IntakeLog(BaseModel):
    date: date
    amount_cups: float

class Goal(BaseModel):
    date: date
    daily_goal_cups: float

def get_all_logs(sheet):
    return sheet.get_all_records()

def add_log_to_sheet(sheet, log):
    sheet.append_row([log.date.strftime("%Y-%m-%d"), log.amount_cups, ""])

def get_logs_by_date_range(sheet, start_date, end_date):
    logs = get_all_logs(sheet)
    filtered_logs = [log for log in logs if start_date <= datetime.strptime(log['Date'], "%Y-%m-%d").date() <= end_date]
    return filtered_logs

def get_goal_by_date(sheet, log_date):
    logs = get_all_logs(sheet)
    for log in logs:
        if log['Date'] == log_date.strftime("%Y-%m-%d"):
            return float(log['Daily Goal'])
    return None

def set_goal(sheet, goal):
    logs = get_all_logs(sheet)
    for i, log in enumerate(logs):
        if log['Date'] == goal.date.strftime("%Y-%m-%d"):
            sheet.update_cell(i + 2, 3, goal.daily_goal_cups)
            return
    sheet.append_row([goal.date.strftime("%Y-%m-%d"), "", goal.daily_goal_cups])

def update_intake_log(sheet, log):
    logs = get_all_logs(sheet)
    for i, log_entry in enumerate(logs):
        if log_entry['Date'] == log.date.strftime("%Y-%m-%d"):
            sheet.update_cell(i + 2, 2, log.amount_cups)
            return
    add_log_to_sheet(sheet, log)

@water_intake_router.post("/log", response_model=IntakeLog)
def log_intake(log: IntakeLog):
    update_intake_log(intake_sheet, log)
    return log

@water_intake_router.get("/logs", response_model=List[IntakeLog])
def get_logs():
    logs = get_all_logs(intake_sheet)
    return logs

@water_intake_router.get("/logs/daily", response_model=List[IntakeLog])
def get_daily_logs(date: date):
    logs = get_logs_by_date_range(intake_sheet, date, date)
    return logs

@water_intake_router.get("/logs/weekly", response_model=List[IntakeLog])
def get_weekly_logs(date: date):
    start_date = date - timedelta(days=date.weekday())  # Monday of the current week
    end_date = start_date + timedelta(days=6)  # Sunday of the current week
    logs = get_logs_by_date_range(intake_sheet, start_date, end_date)
    return logs

@water_intake_router.get("/logs/monthly", response_model=List[IntakeLog])
def get_monthly_logs(date: date):
    start_date = date.replace(day=1)  # First day of the current month
    next_month = (start_date + timedelta(days=31)).replace(day=1)
    end_date = next_month - timedelta(days=1)  # Last day of the current month
    logs = get_logs_by_date_range(intake_sheet, start_date, end_date)
    return logs

@water_intake_router.get("/progress")
def get_progress(date: date):
    daily_logs = get_logs_by_date_range(intake_sheet, date, date)
    total_intake = sum(float(log['Amount']) for log in daily_logs)
    daily_goal = get_goal_by_date(intake_sheet, date)

    if not daily_goal:
        previous_date = date - timedelta(days=1)
        daily_goal = get_goal_by_date(intake_sheet, previous_date) or 8

    progress = (total_intake / daily_goal) * 100 if daily_goal else 0

    return {"date": date, "total_intake_cups": total_intake, "daily_goal_cups": daily_goal, "progress": progress}

@water_intake_router.post("/goal", response_model=Goal)
def set_daily_goal(goal: Goal):
    set_goal(intake_sheet, goal)
    return goal

@water_intake_router.put("/goal", response_model=Goal)
def update_daily_goal(goal: Goal):
    set_goal(intake_sheet, goal)
    return goal

@water_intake_router.delete("/log/undo", response_model=IntakeLog)
def undo_last_log():
    logs = get_all_logs(intake_sheet)
    if not logs:
        raise HTTPException(status_code=404, detail="No logs to undo")
    last_log = logs[-1]
    intake_sheet.delete_row(len(logs) + 1)
    return {"date": datetime.strptime(last_log['Date'], "%Y-%m-%d").date(), "amount_cups": float(last_log['Amount'])}
