from fastapi import FastAPI
from app.database import run_migrations
from app.routers import auth, tasks

app = FastAPI()

run_migrations()

app.include_router(auth.router)
app.include_router(tasks.router)
