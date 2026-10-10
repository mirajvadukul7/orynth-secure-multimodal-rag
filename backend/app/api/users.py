from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def list_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id != "ADMIN" and current_user.role_id != "HR":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(models.User).all()
    return {"users": users}
