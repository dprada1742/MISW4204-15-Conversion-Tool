from fastapi import HTTPException, status
from api.schemas import SignUpRequest


def validate_password(sign_up_request: SignUpRequest):
    if sign_up_request.password1 != sign_up_request.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
