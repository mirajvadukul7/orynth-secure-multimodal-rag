import os
import sys
import uuid
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from app.database.connection import SessionLocal, engine
from app.database import models
from app.auth.security import get_password_hash
from app.retrieval.vector_store import init_qdrant, qdrant_client
from qdrant_client.http import models as qmodels

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    # Clear existing
    db.query(models.AuditLog).delete()
    db.query(models.RecordPermission).delete()
    db.query(models.StructuredRecord).delete()
    db.query(models.Chunk).delete()
    db.query(models.DocumentPermission).delete()
    db.query(models.Document).delete()
    db.query(models.EmployeeData).delete()
    db.query(models.User).delete()
    db.query(models.Department).delete()
    db.query(models.Role).delete()
    
    # Roles
    roles = [
        {"id": "ADMIN", "name": "Admin", "description": "Full access"},
        {"id": "HR", "name": "HR", "description": "HR department access"},
        {"id": "FINANCE", "name": "Finance", "description": "Finance access"},
        {"id": "MANAGER", "name": "Manager", "description": "Managerial access"},
        {"id": "EMPLOYEE", "name": "Employee", "description": "Standard employee access"},
        {"id": "GUEST", "name": "Guest", "description": "Public access only"}
    ]
    for r in roles:
        db.add(models.Role(**r))
        
    # Departments
    departments = [
        {"id": "HR", "name": "Human Resources"},
        {"id": "FINANCE", "name": "Finance"},
        {"id": "ENGINEERING", "name": "Engineering"},
        {"id": "SALES", "name": "Sales"},
        {"id": "LEGAL", "name": "Legal"}
    ]
    for d in departments:
        db.add(models.Department(**d))
        
    db.commit()

    # Users
    users = [
        {"id": str(uuid.uuid4()), "username": "admin", "email": "admin@novacore.com", "role_id": "ADMIN", "department_id": None},
        {"id": str(uuid.uuid4()), "username": "hr_user", "email": "hr@novacore.com", "role_id": "HR", "department_id": "HR"},
        {"id": str(uuid.uuid4()), "username": "finance_user", "email": "finance@novacore.com", "role_id": "FINANCE", "department_id": "FINANCE"},
        {"id": str(uuid.uuid4()), "username": "manager_user", "email": "manager@novacore.com", "role_id": "MANAGER", "department_id": "ENGINEERING"},
        {"id": str(uuid.uuid4()), "username": "employee_user", "email": "employee@novacore.com", "role_id": "EMPLOYEE", "department_id": "ENGINEERING"},
        {"id": str(uuid.uuid4()), "username": "guest_user", "email": "guest@example.com", "role_id": "GUEST", "department_id": None}
    ]
    
    for u in users:
        u["password_hash"] = get_password_hash("password123")
        db.add(models.User(**u))
        
    db.commit()

    # Employee Data (Structured)
    emp_data = [
        {"id": "EMP-001", "name": "admin", "salary": 150000, "department": "Management"},
        {"id": "EMP-002", "name": "hr_user", "salary": 90000, "department": "HR"},
        {"id": "EMP-003", "name": "finance_user", "salary": 95000, "department": "Finance"},
        {"id": "EMP-004", "name": "manager_user", "salary": 120000, "department": "Engineering"},
        {"id": "EMP-005", "name": "employee_user", "salary": 85000, "department": "Engineering"},
        {"id": "EMP-006", "name": "Rahul", "salary": 85000, "department": "Engineering"},
    ]
    for e in emp_data:
        db.add(models.EmployeeData(**e))
        
    db.commit()
    
    # Initialize Qdrant
    try:
        init_qdrant()
        # Ensure collection is fresh
        qdrant_client.delete_collection("aegisrag")
        init_qdrant()
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")

    # Dummy documents and vectors
    # DOC-018: HR_Policy.pdf (Public / ALL EMPLOYEES)
    doc_1 = models.Document(
        id="DOC-018", source_id="SRC-018", filename="HR_Policy.pdf", document_type="pdf",
        department_id="HR", classification="PUBLIC", owner_id=users[1]["id"], file_path="/data/pdfs/HR_Policy.pdf"
    )
    db.add(doc_1)
    
    # Chunk for DOC-018
    chunk_1 = models.Chunk(
        id=str(uuid.uuid4()), document_id="DOC-018", chunk_id="CHUNK-018-03",
        text="The annual leave policy provides 20 days of paid time off per year.", page_number=4,
        metadata={"allowed_roles": ["EMPLOYEE", "MANAGER", "HR", "ADMIN", "FINANCE"]}
    )
    db.add(chunk_1)
    
    # Vector for chunk 1
    try:
        qdrant_client.upsert(
            collection_name="aegisrag",
            points=[
                qmodels.PointStruct(
                    id=1,
                    vector=[0.1] * 384,
                    payload={
                        "source_id": "SRC-018",
                        "document_id": "DOC-018",
                        "chunk_id": "CHUNK-018-03",
                        "department": "HR",
                        "classification": "PUBLIC",
                        "allowed_roles": ["EMPLOYEE", "MANAGER", "HR", "ADMIN", "FINANCE"],
                        "allowed_users": [],
                        "page": 4,
                        "source_type": "pdf",
                        "filename": "HR_Policy.pdf",
                        "text": chunk_1.text
                    }
                )
            ]
        )
    except Exception as e:
        print(f"Error upserting vector 1: {e}")

    # OCR Image: invoice_001.png
    doc_2 = models.Document(
        id="DOC-IMG-001", source_id="SRC-IMG-001", filename="invoice_001.png", document_type="image",
        department_id="FINANCE", classification="CONFIDENTIAL", owner_id=users[2]["id"], file_path="/data/images/invoice_001.png"
    )
    db.add(doc_2)
    
    chunk_2 = models.Chunk(
        id=str(uuid.uuid4()), document_id="DOC-IMG-001", chunk_id="CHUNK-IMG-001-01",
        text="The invoice amount in invoice_001 is $1,250.00.", page_number=1,
        metadata={"allowed_roles": ["FINANCE", "ADMIN"]}
    )
    db.add(chunk_2)

    try:
        qdrant_client.upsert(
            collection_name="aegisrag",
            points=[
                qmodels.PointStruct(
                    id=2,
                    vector=[0.1] * 384,
                    payload={
                        "source_id": "SRC-IMG-001",
                        "document_id": "DOC-IMG-001",
                        "chunk_id": "CHUNK-IMG-001-01",
                        "department": "FINANCE",
                        "classification": "CONFIDENTIAL",
                        "allowed_roles": ["FINANCE", "ADMIN"],
                        "allowed_users": [],
                        "page": 1,
                        "source_type": "image",
                        "filename": "invoice_001.png",
                        "text": chunk_2.text
                    }
                )
            ]
        )
    except Exception as e:
        print(f"Error upserting vector 2: {e}")

    db.commit()
    print("Database seeded successfully with demo users, roles, departments, documents, and qdrant vectors.")

if __name__ == "__main__":
    seed_data()
