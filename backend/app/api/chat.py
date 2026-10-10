from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.auth.dependencies import get_current_user
from app.database import models
from pydantic import BaseModel
from app.rag.orchestrator import process_query

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: list
    grounding_score: float
    security_status: str
    llm_exposure: int
    evidence: list = []

@router.post("/query", response_model=ChatResponse)
def handle_query(req: QueryRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = process_query(req.query, current_user, db)
    return result
