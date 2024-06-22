# Water Intake Tracking App
## Overview
The Water Intake Tracking App helps users monitor and maintain their daily water intake. By setting personalized goals and providing reminders, the app ensures users stay hydrated throughout the day. The app features a user-friendly interface built with Appsmith, a backend hosted on Render, and integration with Google Sheets for data storage.

## Features
- Set personalized daily water intake goals
- Log daily water consumption easily
- View daily, weekly, and monthly hydration progress
- Integration with Google Sheets for data storage
- User-friendly interface

## Technologies Used
- Appsmith: For creating the user interface
- Render: For hosting the backend
- Google Sheets: For storing user data

## Requirements
- Appsmith account
- Render account
- Google Sheets API credentials

## Installation
### Prerequisites
1. Appsmith Setup:

- Sign up for an Appsmith account at Appsmith.
- Create a new application for the Water Intake Tracking App.

2. Render Setup:

- Sign up for a Render account at Render.
- Create a new backend service for handling the app’s logic and connecting to Google Sheets.

3. Google Sheets API Setup:

- Enable the Google Sheets API in the Google Cloud Console.
- Create credentials and obtain the API key and OAuth 2.0 client ID.

### Backend Setup
1. Clone the repository:

git clone https://github.com/your-username/water-intake-tracking.git
cd water-intake-tracking

2. Install dependencies:

pip install -r requirements.txt

3. Configure Google Sheets API:

- Add your client_secret.json file to the project directory.
- Ensure the config.py file contains your Google Sheets spreadsheet ID and necessary configurations.

4. Deploy the backend to Render:

- Follow the Render deployment guide to deploy your backend service.
- Ensure your service URL is noted for connecting with the Appsmith frontend.

### Frontend Setup
1. In Appsmith, design your UI:

- Create input fields for logging water intake.
- Design progress bars or charts to display hydration progress.
- Add buttons and forms for setting goals and viewing history.

2. Connect Appsmith to the Render backend:

- Use Appsmith’s API connector to integrate with your backend endpoints on Render.
- Ensure the endpoints handle requests for logging intake, fetching data, and setting goals.

3. Integrate with Google Sheets:

- Use the backend endpoints to read and write data to Google Sheets.
- Ensure proper authentication and data handling as per your Google Sheets API setup.

## Usage
- Set Daily Goal: Input your daily water intake goal.
- Log Intake: Enter the amount of water consumed throughout the day.
- View Progress: Monitor your hydration progress with visual charts.
