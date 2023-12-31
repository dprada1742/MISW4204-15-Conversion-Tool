from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.security import create_access_token
from app.crud import create_user, verify_credentials
from app.schemas import SignUpRequest
from app.database import get_db

router = APIRouter()


@router.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(sign_up_request: SignUpRequest, db: Session = Depends(get_db)):
    if sign_up_request.password1 != sign_up_request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
    user = create_user(
        db, sign_up_request.username, sign_up_request.email, sign_up_request.password1
    )
    return {"message": "Account successfully created"}


@router.post("/api/auth/login", response_model=dict)
async def login(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = verify_credentials(db, username, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
