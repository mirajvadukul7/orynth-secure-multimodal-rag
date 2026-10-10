import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from dotenv import load_dotenv

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "memory")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL == "memory":
    qdrant_client = QdrantClient(":memory:")
else:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def init_qdrant():
    try:
        qdrant_client.get_collection("aegisrag")
    except Exception:
        qdrant_client.create_collection(
            collection_name="aegisrag",
            vectors_config=qmodels.VectorParams(size=384, distance=qmodels.Distance.COSINE),
        )

def get_permission_filter(user, db):
    # This filter ensures Qdrant only returns chunks authorized for this user
    # 1. Documents where classification is public
    # 2. OR Documents explicitly allowed for user's role
    # 3. OR Documents explicitly allowed for user
    # Simplified version for demo:
    should_conditions = [
        qmodels.FieldCondition(key="classification", match=qmodels.MatchValue(value="PUBLIC")),
    ]
    if user.role_id == "ADMIN":
        # ADMIN can see everything
        return qmodels.Filter()
    
    if user.role_id:
        should_conditions.append(
            qmodels.FieldCondition(key="allowed_roles", match=qmodels.MatchValue(value=user.role_id))
        )
    
    should_conditions.append(
        qmodels.FieldCondition(key="allowed_users", match=qmodels.MatchValue(value=user.id))
    )

    return qmodels.Filter(should=should_conditions)

def search_vectors(query_vector, user, db, limit=5):
    permission_filter = get_permission_filter(user, db)
    results = qdrant_client.search(
        collection_name="aegisrag",
        query_vector=query_vector,
        query_filter=permission_filter,
        limit=limit,
        with_payload=True
    )
    return results
