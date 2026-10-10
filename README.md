# AegisRAG - Secure Intelligence. Permission-Aware Answers.

## Problem Statement
"Secure Multi-Modal RAG System with Access Control"

AegisRAG is a secure Retrieval-Augmented Generation (RAG) system that enforces document-level and row-level authorization **before** retrieval.

### Why AegisRAG is different
Most RAG systems blindly retrieve documents and append them to an LLM prompt. If a user asks for someone else's salary, standard systems might fetch the record, pass it to the LLM, and prompt the LLM to "deny access." 

This is fundamentally flawed. **The LLM is not a security boundary.**

AegisRAG solves this by ensuring:
**"NO AUTHORIZATION → NO RETRIEVAL → NO LLM EXPOSURE → NO LEAKAGE"**

### Architecture
- **Authentication**: JWT-based secure authentication.
- **Authorization Engine**: Validates RBAC, Document ACL, and Row-Level Permissions.
- **Retrieval Orchestrator**: Uses Qdrant metadata filters and SQL-level RLS so the system physically cannot retrieve unauthorized chunks.
- **Evidence Pack**: An isolated evidence bundle passed to the LLM.
- **LLM**: Strict evidence-only generation.
- **Citation Validator**: Validates that all citations refer to authorized chunks.
- **Grounding Verifier**: Calculates a grounding score for answers.

### Features Built
1. Login & JWT Authentication
2. RBAC & Document ACL
3. Row-level Structured Database Authorization
4. Qdrant Permission-Aware Retrieval
5. Vector & Structured Hybrid Retrieval
6. Evidence-only LLM inference (Deterministic Demo Mode)
7. Exact citations & Citation Validation
8. Grounding Score Evaluation
9. Audit Logging
10. Security Test Lab & Dashboard

### Local Setup
Since Docker was unavailable on the test system, the system uses SQLite and an in-memory Qdrant Client by default for ease of demonstration.

1. **Backend**
```bash
cd backend
pip install -r requirements.txt
python scripts/seed_demo.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. **Frontend**
```bash
cd frontend
npm install
npm run dev
```
Access at `http://localhost:3000`

### Demo Accounts
- **Admin**: `admin` / `password123`
- **Employee**: `employee_user` / `password123`
- **HR**: `hr_user` / `password123`

### Hackathon Demo Sequence
1. Log in as `employee_user`.
2. Ask: "What is Rahul's salary?" -> Observe ACCESS DENIED and LLM Exposure = 0.
3. Log out, log in as `admin`.
4. Ask: "What is Rahul's salary?" -> Observe ALLOWED and salary returned.
5. Go to Security Test Lab and run automated tests.
6. Check Audit Logs to see the security traces for each query.
