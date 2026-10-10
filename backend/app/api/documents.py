from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database import models
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def list_documents(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id == "ADMIN":
        docs = db.query(models.Document).all()
    else:
        # Simplified for demo: return docs where user is owner or department matches
        docs = db.query(models.Document).filter(
            (models.Document.owner_id == current_user.id) | 
            (models.Document.department_id == current_user.department_id) |
            (models.Document.classification == "PUBLIC")
        ).all()
    return {"documents": docs}
