from fastapi import FastAPI
from users import users_router
from tasks import tasks_router
from google_sheets import sync_tasks_to_sheets

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(tasks_router, prefix="/tasks")

@app.get("/")
def home():
    return {"message": "Welcome to the Basic Student Task Tracker API!"}

@app.get("/sync")
def sync():
    sync_tasks_to_sheets()
    return {"message": "Tasks synced to Google Sheets"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
