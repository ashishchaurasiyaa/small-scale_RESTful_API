# Task Management API

A RESTful API built with Django and Django REST Framework for task management.

## Features
- CRUD operations for tasks.
- JWT-based authentication.
- Task filtering by status.
- Rate-limiting (5 requests/minute).
- PostgreSQL database (Aurora-compatible).
- AWS Lambda simulation for task completion notifications.
- Optional auto-scaling logic.

## Installation
### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

### Steps
1. Clone the repository: https://github.com/ashishchaurasiyaa/small-scale_RESTful_API.git

2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

3. Install dependencies:
pip install django djangorestframework django-rest-framework-simplejwt django-ratelimit django-redis psycopg2-binary boto3 python-decouple


4. Set up environment variables in `.env`:
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=task_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
AWS_REGION=ap-south-1
AWS_SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:123456789012:task-notifications

5. Run migrations: python manage.py migrate

6. Create a superuser: python manage.py createsuperuser

7. Start the server: python manage.py runserver


## API Endpoints
| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| POST   | `/api/token/`             | Obtain JWT token         |
| POST   | `/api/token/refresh/`     | Refresh JWT token        |
| GET    | `/api/tasks/`             | List tasks (?status=pending) |
| POST   | `/api/tasks/`             | Create a task            |
| GET    | `/api/tasks/{id}/`        | Retrieve a task          |
| PUT    | `/api/tasks/{id}/`        | Update a task            |
| DELETE | `/api/tasks/{id}/`        | Delete a task            |
| POST   | `/api/tasks/{id}/mark_completed/` | Mark task as completed |
| GET    | `/api/tasks/ratelimited/` | Rate-limited task list   |

### Example Request

POST /api/tasks/
Authorization: Bearer <token>
Content-Type: application/json
{
"title": "Test Task",
"description": "Test",
"status": "pending"
}


## Database Schema
- **tasks**:
  - `id`: Integer (PK)
  - `title`: CharField (255)
  - `description`: TextField (nullable)
  - `status`: CharField ("pending", "completed")
  - `assigned_to`: ForeignKey to `auth_user` (nullable)
  - `created_at`: DateTimeField (auto)
  - `updated_at`: DateTimeField (auto)

- **Aurora Integration**: Uses PostgreSQL with Django ORM, compatible with AWS Aurora via `DATABASES` settings.

## AWS Lambda Simulation
Task completion triggers a `post_save` signal that logs to `task_manager.log`. Optionally, an SNS notification is sent if `AWS_SNS_TOPIC_ARN` is set.

## Running Tests

python manage.py test


## Auto-Scaling Logic (Optional)
Monitor task creation rate and scale EC2 instances:

if tasks_created_per_minute > 100:
scale_up_instances(1)
elif tasks_created_per_minute < 20:
scale_down_instances(1)

Run `python tasks/auto_scaling.py` to simulate locally.

## Deployment
1. Deploy on AWS EC2:
gunicorn task_manager.wsgi:application --bind 0.0.0.0:8000

2. Configure PostgreSQL/Aurora:
- Update `DATABASES` in `settings.py` with Aurora endpoint:

DATABASES = {
"default": {
"ENGINE": "django.db.backends.postgresql",
"NAME": "task_db",
"USER": "admin",
"PASSWORD": "yourpassword",
"HOST": "your-aurora-endpoint",
"PORT": "5432",
}
}

3. Set environment variables on the server:


export SECRET_KEY=your-secret-key
export DB_HOST=your-aurora-endpoint
export AWS_SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:123456789012:task-notifications

4. Use Nginx as a reverse proxy:

server {
listen 80;
server_name your-domain.com;
location / {
proxy_pass http fenomeni://127.0.0.1:8000;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
}
}

5. Start services:
- Redis: `redis-server`
- Gunicorn: `gunicorn --workers 3 task_manager.wsgi:application`
- Nginx: `sudo systemctl start nginx`