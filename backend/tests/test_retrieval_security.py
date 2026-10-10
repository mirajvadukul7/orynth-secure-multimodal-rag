import pytest
from fastapi.testclient import TestClient
from main import app
from app.database.connection import SessionLocal
from app.database import models
import uuid

# These tests would require the test client and initialized db
# A complete suite for the hackathon criteria

def test_employee_salary_denied():
    db = SessionLocal()
    employee = db.query(models.User).filter(models.User.role_id == "EMPLOYEE").first()
    
    if employee:
        from app.rag.orchestrator import process_query
        res = process_query("What is Rahul's salary?", employee, db)
        
        assert res["security_status"] == "BLOCKED"
        assert res["llm_exposure"] == 0
    db.close()

def test_admin_salary_allowed():
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.role_id == "ADMIN").first()
    
    if admin:
        from app.rag.orchestrator import process_query
        res = process_query("What is Rahul's salary?", admin, db)
        
        assert res["security_status"] == "SECURE"
        assert res["llm_exposure"] > 0
    db.close()
