from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt

from models import Base, User, UserBase, UserLogin

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "cloud_class"
ALGORITHM = "HS256"

@app.post("/api/auth/signup")
def create_user(user: UserBase, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Error: el usuario ya está registrado")

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Error: el correo ya está registrado.")

    if user.password != user.password_confirmation:
        raise HTTPException(status_code=400, detail="Error: las contraseñas no coinciden.")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()

    return JSONResponse(content={"mensaje":"Usuario creado correctamente"}, status_code=201)

@app.post("/api/auth/login")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inválido")        
    if not pwd_context.verify(user_login.password, user.password):
        raise HTTPException(status_code=401, detail="Contraseña inválida")        

    if user and pwd_context.verify(user_login.password, user.password):
        token_data = {"sub": user.username}
        token = create_access_token(token_data)
        return JSONResponse(content={"token": token}, status_code=200)

    raise HTTPException(status_code=401, detail="Credenciales inválidas")

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
