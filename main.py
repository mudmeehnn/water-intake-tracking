from fastapi import FastAPI
from users import users_router
from google_sheets import sync_tasks_to_sheets
from water_intake import water_intake_router  # Ensure this matches the file name where your router is defined

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(water_intake_router, prefix="/water_intake")

@app.get("/")
def home():
    return {"message": "Welcome to the Water Intake Tracker API!"}

@app.get("/sync")
def sync():
    sync_tasks_to_sheets()
    return {"message": "Tasks synced to Google Sheets"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
