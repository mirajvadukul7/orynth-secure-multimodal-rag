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
