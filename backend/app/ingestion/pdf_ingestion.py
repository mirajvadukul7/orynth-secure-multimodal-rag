import uuid
from sqlalchemy.orm import Session
from app.database import models
import fitz  # PyMuPDF
from app.retrieval.vector_store import qdrant_client, get_permission_filter
from qdrant_client.http import models as qmodels

class DummyEmbedder:
    def encode(self, text):
        return [0.1] * 384 # 384-dim dummy vector for demo

embedder = DummyEmbedder()

def ingest_pdf(file_path: str, document_id: str, department: str, classification: str, owner_id: str, db: Session):
    # This is a mocked or simplified implementation for the demo
    doc = fitz.open(file_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        chunk_id = f"CHUNK-{document_id}-{page_num}"
        chunk = models.Chunk(
            id=str(uuid.uuid4()),
            document_id=document_id,
            chunk_id=chunk_id,
            text=text,
            page_number=page_num + 1,
            metadata={"allowed_roles": ["EMPLOYEE", "ADMIN", "HR", "FINANCE", "MANAGER"]}
        )
        db.add(chunk)
        
        vector = embedder.encode(text)
        
        qdrant_client.upsert(
            collection_name="aegisrag",
            points=[
                qmodels.PointStruct(
                    id=abs(hash(chunk_id)),
                    vector=vector,
                    payload={
                        "source_id": f"SRC-{document_id}",
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "department": department,
                        "classification": classification,
                        "allowed_roles": ["EMPLOYEE", "ADMIN", "HR", "FINANCE", "MANAGER"],
                        "allowed_users": [owner_id],
                        "page": page_num + 1,
                        "source_type": "pdf",
                        "text": text
                    }
                )
            ]
        )
    db.commit()
