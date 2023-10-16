from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    username: str
    password1: str
    password2: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str
