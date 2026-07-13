from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

class SecureVectorDB:
    def __init__(self):
        # Connect to the local Qdrant container running on your host
        self.client = QdrantClient(host="127.0.0.1", port=6333)
        # Load local, CPU-friendly embedding model
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = "enterprise_kb"

    def initialize_collection(self):
        """Recreates the vector collection for a clean slate."""
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    def ingest_documents(self, documents):
        """Indexes documents and maps them to security metadata classifications."""
        points = []
        for doc in documents:
            vector = self.embed_model.encode(doc["text"]).tolist()
            points.append(
                PointStruct(
                    id=doc["id"],
                    vector=vector,
                    payload={
                        "text": doc["text"], 
                        "classification": doc["classification"] # e.g., 'public' or 'confidential'
                    }
                )
            )
        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"[+] Successfully indexed {len(documents)} documents into Qdrant.")

    def secure_search(self, query_text, user_clearance):
        """
        Retrieves vector chunks while enforcing clearance-based metadata filtering.
        This represents the RBAC defense mechanism.
        """
        query_vector = self.embed_model.encode(query_text).tolist()
        
        # Security Rule: If the user is not an 'admin', filter out confidential documents
        search_filter = None
        if user_clearance != "admin":
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="classification",
                        match=MatchValue(value="public")
                    )
                ]
            )

      
# Utilizing Qdrant's modern Universal Query API
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,  # query_vector becomes query
            limit=2,
            query_filter=search_filter
        )
        # Unwrap the points from the response payload
        return [point.payload["text"] for point in response.points]
