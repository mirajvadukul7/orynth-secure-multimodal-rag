from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
def get_admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    user_count = db.query(models.User).count()
    doc_count = db.query(models.Document).count()
    chunk_count = db.query(models.Chunk).count()
    
    # Audit stats
    total_queries = db.query(models.AuditLog).count()
    blocked_queries = db.query(models.AuditLog).filter(models.AuditLog.security_decision == "BLOCKED").count()
    
    return {
        "total_users": user_count,
        "total_documents": doc_count,
        "total_chunks": chunk_count,
        "total_vectors": chunk_count, # Assuming 1-to-1
        "queries_today": total_queries,
        "blocked_queries": blocked_queries,
        "security_violations": blocked_queries,
        "average_grounding_score": 98.5 # Demo static value
    }
