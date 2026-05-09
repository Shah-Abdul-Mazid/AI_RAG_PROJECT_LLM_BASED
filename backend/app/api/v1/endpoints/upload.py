import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.agents.retriever import retriever_agent
from app.db.pinecone import vector_store

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # 1. Save file locally
        os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOADS_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # 2. Advanced partitioning using Unstructured
        from app.utils.unstructured_loader import advanced_partition_file
        chunks = advanced_partition_file(file_path)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            vec = retriever_agent._get_embeddings(chunk)
            vectors.append({
                "id": f"doc_{file.filename}_{i}",
                "values": vec,
                "metadata": {"text": chunk, "source": file.filename}
            })
        
        if vectors:
            vector_store.index.upsert(vectors=vectors)

        return {"filename": file.filename, "status": "indexed", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
