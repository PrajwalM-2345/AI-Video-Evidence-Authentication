import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Initialize the official Qdrant REST client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

COLLECTION_NAME = "face_signatures"

def init_vector_db():
    """Scaffolds a facial feature embedding vector index inside Qdrant."""
    try:
        # Check if collection already exists to prevent overwrite drops
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            # Creating collection optimized for Face Recognition models (e.g., ArcFace/Facenet outputting 512-dim vectors)
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=512,  # Standard dimension length for face biometric models
                    distance=Distance.COSINE # Cosine distance is standard for facial match comparisons
                )
            )
            print(f"🚀 Qdrant Vector Collection '{COLLECTION_NAME}' initialized successfully.")
        else:
            print(f"ℹ️ Qdrant Vector Collection '{COLLECTION_NAME}' already active.")
    except Exception as e:
        print(f"⚠️ Vector DB warning during initialization: {str(e)}")