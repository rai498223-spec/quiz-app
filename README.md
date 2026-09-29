# FlowPlan

FlowPlan is a Django productivity dashboard for managing tasks, building a daily timetable, and tracking progress in real time.

## Features

- User authentication and onboarding
- Personal task management with priorities and deadlines
- Daily timetable generation based on user routine
- Dashboard with current task and next task cards
- Calendar and task overview pages
- Settings for routine and reminder preferences

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   python -m pip install -r requirements.txt
3. Copy `.env.example` to `.env` and set `SECRET_KEY` to a secure random value.
4. Run migrations:
   python manage.py migrate
5. Create an admin account:
   python manage.py createsuperuser
6. Start the application:
   python manage.py runserver

## URLs

- Login: /accounts/login/
- Signup: /accounts/signup/
- Dashboard: /dashboard/
- Tasks: /tasks/
- Timetable: /timetable/

## Demo note

The project uses SQLite for development and keeps the user data isolated by user.
