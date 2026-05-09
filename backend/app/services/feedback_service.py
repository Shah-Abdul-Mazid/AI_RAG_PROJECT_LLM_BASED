import hashlib
from app.db.pinecone import vector_store
from app.agents.retriever import retriever_agent

class FeedbackService:
    def save_positive_feedback(self, query: str, answer: str):
        """Stores high-quality Q&A pairs in a separate namespace for 'Reinforcement Learning'"""
        print(f"Saving positive feedback for: {query[:50]}...")
        
        # 1. Generate embedding for the query
        vector = retriever_agent._get_embeddings(query)
        
        # 2. Upsert to a 'gold_standard' namespace
        vector_store.index.upsert(
            vectors=[{
                "id": f"gold_{hashlib.md5(query.encode()).hexdigest()}",
                "values": vector,
                "metadata": {
                    "query": query,
                    "answer": answer,
                    "type": "gold_standard"
                }
            }],
            namespace="feedback_memory"
        )

feedback_service = FeedbackService()
