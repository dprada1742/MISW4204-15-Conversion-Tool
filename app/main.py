from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, tasks

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(tasks.router)
