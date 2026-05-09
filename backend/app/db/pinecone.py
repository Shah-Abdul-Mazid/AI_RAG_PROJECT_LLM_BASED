from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.required_dim = 1536 if settings.LLM_PROVIDER == "openai" else 768
        
        # Auto-recreate on mismatch
        if self.index_name in self.pc.list_indexes().names():
            index_desc = self.pc.describe_index(self.index_name)
            if index_desc.dimension != self.required_dim:
                self.pc.delete_index(self.index_name)
        
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=self.required_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

vector_store = VectorStore()
