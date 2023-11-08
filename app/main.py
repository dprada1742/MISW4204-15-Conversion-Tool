from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.database import run_migrations
from app.routers import auth, tasks
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/healthcheck")
def healthcheck():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"status": "healthy service"}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"Exception caught! {exc}")
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred. {exc}"},
    )


run_migrations()

app.include_router(auth.router)
app.include_router(tasks.router)
