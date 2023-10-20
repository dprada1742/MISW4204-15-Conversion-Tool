# MISW4204-15-Conversion-Tool

This is a FastAPI project that includes user authentication and task management functionalities. The project utilizes FastAPI, SQLAlchemy for interacting with a PostgreSQL database, and Alembic for database migrations. The docker-compose setup takes care of the necessary environment setup, making it easy to get started.

## Setup

### Requirements

- Docker

### Run Project Using Docker

1. **Clone the repository:**
```bash
git clone --branch 1.3.0 https://github.com/dprada1742/MISW4204-15-Conversion-Tool.git
cd MISW4204-15-Conversion-Tool
```

2. **Build and run the Docker containers:**
```bash
docker-compose build
docker-compose up
```

## Usage

Once the Docker containers are up and running, the FastAPI application will be available at [http://localhost:80](http://localhost:80).

You can access the interactive API documentation at [http://localhost:80/docs](http://localhost:80/docs).

## API Endpoints

The API includes the following endpoints:

- **User Authentication**
    - `POST /api/auth/signup`: Sign up a new user.
    - `POST /api/auth/login`: Log in and receive an access token.

- **Task Management**
    - `GET /api/tasks`: Get a list of tasks.
    - `POST /api/tasks`: Create a new task.
    - `GET /api/tasks/{id_task}`: Retrieve details of a specific task.
    - `DELETE /api/tasks/{id_task}`: Delete a specific task.

For more detailed API documentation, you can visit the interactive API documentation at [http://localhost:80/docs](http://localhost:80/docs) once the application is running.
```

This README simplifies the setup process by focusing on the Docker setup, which is what you wanted for the tutor. It avoids the need for manual database setup, Python virtual environment setup, or manual installation of dependencies. The tutor just needs Docker installed, and then they can clone the project, build and run the Docker containers, and access the application and API documentation through their web browser.