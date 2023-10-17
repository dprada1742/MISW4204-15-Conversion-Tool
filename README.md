# MISW4204-15-Conversion-Tool

This is a FastAPI project that includes user authentication and task management functionalities. The project utilizes FastAPI, SQLAlchemy for interacting with a PostgreSQL database, and Alembic for database migrations.

## Setup

### Requirements

- Python 3.8 or higher
- Docker

### Run project using Docker
```bash
docker-compose build
docker-compose up
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dprada1742/MISW4204-15-Conversion-Tool.git
cd MISW4204-15-Conversion-Tool
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Update the DATABASE_URL in database.py with your database connection details.
# Then run:
alembic upgrade head
```

## Usage

Run the FastAPI application:

```bash
uvicorn app.main:app --reload
```


Run celery worker

```bash
celery -A app.celery_app worker --loglevel=info -P gevent
```

## Database Migrations
1. Generate a new migration:

```bash
alembic revision --autogenerate -m "description_of_your_migration"
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). You can access the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Endpoints

- **User Authentication**
    - `POST /auth/signup`: Sign up a new user.
    - `POST /auth/login`: Log in and receive an access token.

- **Task Management**
    - `GET /api/tasks`: Get a list of tasks.
    - `POST /api/tasks`: Create a new task.
    - `GET /api/tasks/{id_task}`: Retrieve details of a specific task.
    - `DELETE /api/tasks/{id_task}`: Delete a specific task.
