from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.retriever import retriever_agent
from app.db.pinecone import vector_store
import requests
from bs4 import BeautifulSoup
from app.api.v1.endpoints.auth import get_current_user
from fastapi import Depends
from app.db.models import User

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

class BulkScrapeRequest(BaseModel):
    urls: list[str]

@router.post("/scrape")
async def scrape_website(
    request: ScrapeRequest,
    current_user: User = Depends(get_current_user)
):
    # Existing logic...
    try:
        return _perform_scrape(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-scrape")
async def bulk_scrape_websites(
    request: BulkScrapeRequest,
    current_user: User = Depends(get_current_user)
):
    """Handles multiple URLs in a single request (Batch Logic)"""
    results = []
    for url in request.urls:
        try:
            chunks = _perform_scrape(url)
            results.append({"url": url, "status": "processed", "chunks": chunks})
        except Exception as e:
            results.append({"url": url, "status": "error", "detail": str(e)})
    return {"results": results}

def _perform_scrape(url: str):
    import hashlib
    print(f"Scraping {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
    
    vectors = []
    for i, chunk in enumerate(chunks):
        unique_id = hashlib.md5(f"{url}_{i}".encode()).hexdigest()
        vec = retriever_agent._get_embeddings(chunk)
        vectors.append({
            "id": f"web_{unique_id}",
            "values": vec,
            "metadata": {"text": chunk, "source": url}
        })
    
    if vectors:
        vector_store.index.upsert(vectors=vectors)
    return len(chunks)
