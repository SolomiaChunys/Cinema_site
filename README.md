# Cinema Website Project

This is a Django-based cinema website project with REST API integration.
The project includes user authentication, session management, and CRUD
operations for cinema halls and movie sessions. The focus is on backend
development using Class-Based Views (CBV) and ensuring the application is
scalable, reliable, and robust.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Celery](#celery)

## Features
- User authentication (login, logout, registration)
- Auto logout for non-admin users after 1 minute of inactivity
- Admin can manage cinema halls and sessions
- Users can view sessions, purchase tickets, and see their purchase history
- REST API for all actions
- Sorting of sessions by price or start time
- Daily database cleanup using Celery

## Required packages
- Python 3.8+
- Django 3.2+ (tests will not work if Django ver. < 4.2)
- djangorestframework (for REST API)
- django-celery-beat (for task planning)
- django-celery-results (to store Celery results)
- Redis (or another message broker for Celery)
- Docker (for containerized deployment)
- psycopg2-binary (for PostgreSQL)
- python-dotenv 1.0.1+ (for .env file)
- pillow (for working with images)

## Installation

### Clone the repository
```bash
git clone https://github.com/SolomiaChunys/Cinema_site.git
cd cinema_proj
```

### Create a virtual environment and activate it
```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Apply migrations
```bash
python manage.py migrate
```

### Create a superuser
```bash
python manage.py createsuperuser
```

### Create an Env File
- Instead of setting environment variables manually, you can use a .env file to centrally manage them. Simply place this file at the root of your project directory. This file is also used to define environment variables for Docker containers, ensuring consistent configurations across different environments.
- Refer to the provided .env.example file as a template for setting up your own .env file. Be sure to customize the variable values according to your project's requirements.

### Run the development server
```bash
python manage.py runserver
```

## Usage
### Admin Actions

- Create Cinema Hall: Specify the hall name and size.
- Create Session: Specify start time, end time, showing dates, and ticket price.
- Edit Hall or Session: Only if no tickets have been sold for that session or hall. 
- Sessions should not overlap in the same hall.

### User Actions

- View Sessions: Check the list of sessions for today and tomorrow, including the number of available seats.
- Buy Tickets: Purchase tickets for a session, with a notification if the hall is full.
- View Purchase History: See the list of all purchases and the total amount spent. 
- Sort Sessions: By price or start time.
- Anonymous User: Can view and sort sessions but cannot purchase tickets.

## Testing

Although tests are optional, they are highly encouraged. To run the tests, use the following commands for both app:
```bash
python manage.py test cinema.tests 
python manage.py test api.tests 
```

## Celery
```bash
celery -A main worker -l INFO --pool=solo (task runner)
celery -A main beat -l INFO
```