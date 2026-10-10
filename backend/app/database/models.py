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
