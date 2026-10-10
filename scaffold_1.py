import os

def create_files(base_path, file_structure):
    for path, content in file_structure.items():
        full_path = os.path.join(base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + '\n')

backend_files = {
    'backend/requirements.txt': '''
fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
qdrant-client
PyMuPDF
sentence-transformers
python-dotenv
httpx
pytest
pillow
pytest-asyncio
''',
    'backend/.env.example': '''
DATABASE_URL=postgresql://aegisrag:password@postgres:5432/aegisrag
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=
JWT_SECRET=super_secret_key_change_me
LLM_PROVIDER=demo
LLM_API_KEY=
EMBEDDING_PROVIDER=local
DEMO_MODE=true
''',
    'backend/main.py': '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api import auth, chat, documents, users, admin, security, health
from app.database.connection import engine
from app.database import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AegisRAG", version="1.0.0", description="Secure Multi-Modal RAG System with Access Control")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
    'backend/app/api/health.py': '''
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def health_check():
    return {"status": "ok"}
''',
    'docker-compose.yml': '''
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: aegisrag
      POSTGRES_PASSWORD: password
      POSTGRES_DB: aegisrag
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: 
      context: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://aegisrag:password@postgres:5432/aegisrag
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - postgres
      - qdrant
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
  qdrant_data:
''',
    'backend/Dockerfile': '''
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
'''
}

if __name__ == "__main__":
    create_files("d:/PHP/AegisRAG", backend_files)
    print("Project scaffolded successfully.")
