import os

def create_files(base_path, file_structure):
    for path, content in file_structure.items():
        full_path = os.path.join(base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')

backend_files = {
    'backend/app/database/connection.py': '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aegisrag:password@localhost:5432/aegisrag")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
    'backend/app/database/models.py': '''
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role_id = Column(String, ForeignKey("roles.id"))
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role")
    department = relationship("Department")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    source_id = Column(String, unique=True, index=True)
    filename = Column(String)
    document_type = Column(String)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    classification = Column(String)
    owner_id = Column(String, ForeignKey("users.id"))
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    department = relationship("Department")

class DocumentPermission(Base):
    __tablename__ = "document_permissions"
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    role_id = Column(String, ForeignKey("roles.id"), nullable=True)
    permission_type = Column(String) # READ, WRITE

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_id = Column(String, unique=True)
    text = Column(Text)
    page_number = Column(Integer, nullable=True)
    metadata = Column(JSON)

class StructuredRecord(Base):
    __tablename__ = "structured_records"
    id = Column(String, primary_key=True, index=True)
    table_name = Column(String)
    record_id = Column(String)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    classification = Column(String)
    owner_id = Column(String, ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON)

class RecordPermission(Base):
    __tablename__ = "record_permissions"
    id = Column(String, primary_key=True, index=True)
    record_id = Column(String, ForeignKey("structured_records.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    role_id = Column(String, ForeignKey("roles.id"), nullable=True)
    permission_type = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    query = Column(String)
    retrieved_count = Column(Integer)
    authorized_count = Column(Integer)
    denied_count = Column(Integer)
    llm_exposure_count = Column(Integer)
    citations = Column(JSON)
    security_decision = Column(String)
    grounding_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class EmployeeData(Base):
    __tablename__ = "employees_data"
    id = Column(String, primary_key=True)
    name = Column(String)
    salary = Column(Integer)
    department = Column(String)
''',
    'backend/app/auth/security.py': '''
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
''',
    'backend/app/auth/dependencies.py': '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.auth.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
''',
    'backend/app/api/auth.py': '''
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.auth.security import verify_password, create_access_token
from app.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role_id: str

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.id, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role_id": current_user.role_id
    }
'''
}

if __name__ == "__main__":
    create_files("d:/PHP/AegisRAG", backend_files)
    print("Database and auth scaffolded successfully.")
