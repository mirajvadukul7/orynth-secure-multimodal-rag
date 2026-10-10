import uuid
from app.database import models
from app.retrieval.vector_store import search_vectors
from app.rag.llm_provider import generate_answer
from app.rag.citation_validator import validate_citations
from sqlalchemy.orm import Session
from datetime import datetime

class DummyEmbedder:
    def encode(self, text):
        return [0.1] * 384 # 384-dim dummy vector for demo

embedder = DummyEmbedder()

def process_query(query: str, user: models.User, db: Session):
    # 1. Generate Query Vector
    query_vector = embedder.encode(query)
    
    # 2. Qdrant Vector Retrieval with Permission Filter
    vector_results = search_vectors(query_vector, user, db, limit=5)
    
    # 3. Structured Data Retrieval (Row Level Security)
    structured_results = retrieve_structured_data(query, user, db)

    # 4. Construct Evidence Pack (ONLY AUTHORIZED)
    evidence_pack = []
    
    for hit in vector_results:
        payload = hit.payload
        evidence_pack.append({
            "source_id": payload.get("source_id"),
            "source_type": payload.get("source_type"),
            "document": payload.get("filename"),
            "page": payload.get("page"),
            "chunk_id": payload.get("chunk_id"),
            "text": payload.get("text")
        })

    for rec in structured_results:
        evidence_pack.append({
            "source_id": f"SRC-DB-{rec.table_name}-{rec.record_id}",
            "source_type": "database",
            "document": rec.table_name,
            "page": None,
            "chunk_id": rec.record_id,
            "text": f"Table: {rec.table_name}, Record ID: {rec.record_id}, Data: {rec.metadata}"
        })

    # Security check: If no evidence, return early
    if not evidence_pack:
        log_audit(db, user.id, query, 0, 0, "BLOCKED", 0, [], 0)
        return {
            "answer": "ACCESS DENIED or I don't have enough authorized evidence to answer that.",
            "citations": [],
            "grounding_score": 0,
            "security_status": "BLOCKED",
            "llm_exposure": 0
        }

    # 5. LLM Generation
    llm_response = generate_answer(query, evidence_pack)

    # 6. Citation Validation
    valid_citations = validate_citations(llm_response["citations"], evidence_pack)
    
    # 7. Grounding Score
    grounding_score = len(valid_citations) / len(llm_response["citations"]) * 100 if llm_response["citations"] else 100
    
    # 8. Audit Logging
    log_audit(db, user.id, query, len(evidence_pack), len(evidence_pack), "SECURE", len(evidence_pack), valid_citations, grounding_score)
    
    return {
        "answer": llm_response["answer"],
        "citations": valid_citations,
        "grounding_score": grounding_score,
        "security_status": "SECURE",
        "llm_exposure": len(evidence_pack),
        "evidence": evidence_pack
    }

def retrieve_structured_data(query: str, user: models.User, db: Session):
    # A mocked SQL structured retrieval with RLS
    results = []
    
    # If the user asks about salary, we must enforce row-level security
    if "salary" in query.lower():
        # RLS: Users can only see their own salary, unless ADMIN or HR
        if user.role_id in ["ADMIN", "HR"]:
            records = db.query(models.EmployeeData).all()
        else:
            records = db.query(models.EmployeeData).filter(models.EmployeeData.name.ilike(f"%{user.username}%")).all()
            
        for r in records:
            results.append(
                type('obj', (object,), {'table_name': 'employees', 'record_id': r.id, 'metadata': {'name': r.name, 'salary': r.salary, 'department': r.department}})()
            )
    return results

def log_audit(db, user_id, query, retrieved, authorized, decision, exposure, citations, score):
    log = models.AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        query=query,
        retrieved_count=retrieved,
        authorized_count=authorized,
        denied_count=retrieved - authorized,
        llm_exposure_count=exposure,
        citations=citations,
        security_decision=decision,
        grounding_score=score
    )
    db.add(log)
    db.commit()
