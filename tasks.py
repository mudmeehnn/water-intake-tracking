import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import json

credentials_json = os.getenv('GOOGLE_CREDENTIALS')
GOOGLE_SHEETS_CREDENTIALS = json.loads(credentials_json)

TASK_SPREADSHEET_NAME = 'TasksDatabase'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
client = gspread.authorize(creds)
task_sheet = client.open(TASK_SPREADSHEET_NAME).sheet1

tasks_router = APIRouter()

class Task(BaseModel):
    title: str
    description: str
    completed: bool = False

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

def get_all_tasks():
    return task_sheet.get_all_records()

def add_task_to_sheet(task):
    task_sheet.append_row([task.title, task.description, task.completed])

def update_task_in_sheet(task_id, task):
    cell = task_sheet.find(task_id)
    task_sheet.update_cell(cell.row, 2, task.title)
    task_sheet.update_cell(cell.row, 3, task.description)
    task_sheet.update_cell(cell.row, 4, task.completed)

def delete_task_from_sheet(task_id):
    cell = task_sheet.find(task_id)
    task_sheet.delete_row(cell.row)

@tasks_router.post("/", response_model=Task)
def add_task(task: Task):
    add_task_to_sheet(task)
    return task

@tasks_router.get("/", response_model=List[Task])
def get_tasks():
    tasks = get_all_tasks()
    return tasks

@tasks_router.put("/{id}", response_model=Task)
def update_task(id: int, task: TaskUpdate):
    existing_task = next((t for t in get_all_tasks() if t['id'] == id), None)

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_task_in_sheet(id, task)

    return task

@tasks_router.delete("/{id}")
def delete_task(id: int):
    delete_task_from_sheet(id)
    return {"message": "Task deleted successfully"}

@tasks_router.get("/progress")
def get_progress():
    tasks = get_all_tasks()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['completed'] == 'True')

    progress = (completed_tasks / total_tasks) * 100 if total_tasks else 0

    return {"total_tasks": total_tasks, "completed_tasks": completed_tasks, "progress": progress}
