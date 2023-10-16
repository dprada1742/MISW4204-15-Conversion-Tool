from fastapi import FastAPI
from api.routers import auth
from db.session import init_db

app = FastAPI()

init_db()

app.include_router(auth.router)
