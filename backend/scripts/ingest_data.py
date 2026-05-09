import os
import sys

# Fix path to import 'app' from parent directory
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

from app.db.pinecone import vector_store
from app.agents.retriever import retriever_agent
from app.utils.unstructured_loader import advanced_partition_file

DATA_DIR = os.path.abspath(os.path.join(os.getcwd(), "../../data"))

def ingest_all():
    print(f"Scanning directory: {DATA_DIR}")
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(file_path):
            print(f"Ingesting: {filename}")
            chunks = advanced_partition_file(file_path)
            
            vectors = []
            for i, chunk in enumerate(chunks):
                vec = retriever_agent._get_embeddings(chunk)
                vectors.append({
                    "id": f"static_{filename}_{i}",
                    "values": vec,
                    "metadata": {"text": chunk, "source": filename}
                })
            
            if vectors:
                vector_store.index.upsert(vectors=vectors)
            print(f"✅ Indexed {filename}")

if __name__ == "__main__":
    ingest_all()
