from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import run_migrations
from app.routers import auth, tasks
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"Exception caught! {exc}")
    logger.exception(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred. {exc}"},
    )


run_migrations()

app.include_router(auth.router)
app.include_router(tasks.router)
