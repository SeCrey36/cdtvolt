# Education Platform API

## Quick Start

### Requirements
- Python 3.8+
- Django 4.2+
- PostgreSQL

## Installation

### Clone repository
git clone <repository-url>
cd education_platform

### Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
### or
venv\Scripts\activate     # Windows

### Install dependencies
pip install -r requirements.txt

### Configure database
python manage.py migrate

### Create superuser
python manage.py createsuperuser

### Run server
python manage.py runserver

## Swagger use
Open http://localhost:8000/swagger/
Find your endpoint in the list
Click "Try it out" to activate testing
Enter required data
Click "Execute" to send request
View response below

### Authentication
Get JWT token via /api/auth/login/
Click "Authorize" button in Swagger
Enter: Bearer your_token
Save to access protected endpoints