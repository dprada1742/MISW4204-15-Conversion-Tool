from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.crud import create_user
from api.dependencies import validate_password
from api.schemas import SignUpRequest

router = APIRouter()


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(sign_up_request: SignUpRequest, db: Session = Depends(get_db)):
    validate_password(sign_up_request)
    user = create_user(
        db, sign_up_request.username, sign_up_request.email, sign_up_request.password1
    )
    return {"message": "Account successfully created"}
