from fastapi import FastAPI
from api.routers import auth, tasks
from db.session import init_db

app = FastAPI()

init_db()

app.include_router(auth.router)
app.include_router(tasks.router)
