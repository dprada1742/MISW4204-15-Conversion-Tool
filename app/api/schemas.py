from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    username: str
    password1: str
    password2: str
    email: EmailStr
