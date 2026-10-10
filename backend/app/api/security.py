from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import models
from app.auth.dependencies import get_current_user
from app.rag.orchestrator import process_query

router = APIRouter()

@router.get("/tests")
def get_security_tests(current_user: models.User = Depends(get_current_user)):
    return {
        "tests": [
            {"id": "TEST-1", "name": "Employee accesses public document", "expected": "PASS"},
            {"id": "TEST-2", "name": "Employee accesses HR confidential document", "expected": "DENIED"},
            {"id": "TEST-3", "name": "HR accesses HR document", "expected": "ALLOWED"},
            {"id": "TEST-4", "name": "Finance accesses HR document", "expected": "DENIED"},
            {"id": "TEST-5", "name": "Employee asks for another employee's salary", "expected": "DENIED"},
            {"id": "TEST-6", "name": "Admin asks for employee salary", "expected": "ALLOWED"}
        ]
    }

@router.post("/tests/run")
def run_security_tests(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only test runner")
    
    # We will simulate requests as different users here for the test suite
    results = []
    
    users = {
        "EMPLOYEE": db.query(models.User).filter(models.User.role_id == "EMPLOYEE").first(),
        "HR": db.query(models.User).filter(models.User.role_id == "HR").first(),
        "FINANCE": db.query(models.User).filter(models.User.role_id == "FINANCE").first(),
        "ADMIN": current_user
    }
    
    # TEST 1
    res1 = process_query("What is the annual leave policy?", users["EMPLOYEE"], db)
    results.append({"id": "TEST-1", "status": "PASS" if res1["security_status"] == "SECURE" else "FAIL"})
    
    # TEST 5
    res5 = process_query("What is Rahul's salary?", users["EMPLOYEE"], db)
    results.append({"id": "TEST-5", "status": "PASS" if res5["security_status"] == "BLOCKED" and res5["llm_exposure"] == 0 else "FAIL"})
    
    # TEST 6
    res6 = process_query("What is Rahul's salary?", users["ADMIN"], db)
    results.append({"id": "TEST-6", "status": "PASS" if res6["security_status"] == "SECURE" else "FAIL"})
    
    return {"results": results}

@router.get("/audit")
def get_audit_logs(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role_id != "ADMIN":
        # Non-admins can only see their own audit logs
        logs = db.query(models.AuditLog).filter(models.AuditLog.user_id == current_user.id).order_by(models.AuditLog.timestamp.desc()).all()
    else:
        logs = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).all()
        
    return {"logs": logs}
