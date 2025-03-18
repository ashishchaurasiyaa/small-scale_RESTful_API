Task Management API
A RESTful API for a simple task management system built with Django and Django REST Framework (DRF). It includes user authentication, task management, filtering, rate limiting, and AWS integration simulation.


Features
CRUD Operations: Create, Read, Update, and Delete tasks.
Authentication: Token-based authentication using Django’s built-in auth system.
Task Filtering: Filter tasks by status (e.g., pending, completed).
Rate Limiting: Implements rate-limiting using Django’s cache framework.
Database: Uses PostgreSQL, compatible with AWS Aurora DB.
AWS Integration Simulation: Simulates an AWS Lambda function to log notifications when a task is marked as completed.
Scalability: Designed to scale efficiently with task volume.

Installation
Prerequisites
Python 3.10+
PostgreSQL
Redis (for caching and rate limiting)

Clone the Repository:

git clone https://github.com/ashishchaurasiyaa/small-scale_RESTful_API.git  
cd small-scale_RESTful_API  

Create and Activate Virtual Environment:

python -m venv venv  
source venv/bin/activate  # For Linux/macOS  
venv\Scripts\activate  # For Windows  


Install Dependencies:
pip install -r requirements.txt

Configure Environment Variables

SECRET_KEY=your_secret_key  
DEBUG=True  
DATABASE_URL=postgres://user:password@localhost:5432/task_db  


Run Migrations:
python manage.py migrate

Create a Superuser

python manage.py createsuperuser

Start the Server:

python manage.py runserver  

API Endpoints:

POST	/api/tasks/	Create a new task
GET	/api/tasks/	Retrieve all tasks
GET	/api/tasks/{id}/	Retrieve a single task
PUT	/api/tasks/{id}/	Update a task
DELETE	/api/tasks/{id}/	Delete a task
GET	/api/tasks?status=pending	Filter tasks by status

Simulating AWS Lambda
A local function is triggered when a task is marked as completed. This mimics an AWS Lambda function logging task completion.

Running Tests:
To run unit tests, execute:


Deployment
For production, use Gunicorn and set up an EC2 instance or a containerized environment

gunicorn task_manager.wsgi:application --bind 0.0.0.0:8000  

Auto-Scaling (Bonus)
To handle increasing task volume, implement an auto-scaling logic using AWS EC2 Auto Scaling or Kubernetes Horizontal Pod Autoscaler.



