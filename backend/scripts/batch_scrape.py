import sys
import os
import hashlib
import requests
from bs4 import BeautifulSoup

# Fix path to import 'app' from parent directory
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

from app.agents.retriever import retriever_agent
from app.db.pinecone import vector_store
from app.core.config import settings

URLS = [
    "https://www.mgi.org/",
    "https://www.mgi.org/career",
    "https://www.mgi.org/who-we-are/board-of-director",
    "https://www.mgi.org/about",
    "https://www.mgi.org/who-we-are/leadership-team",
    "https://en.wikipedia.org/wiki/Meghna_Group_of_Industries",
    "https://bn.wikipedia.org/wiki/%E0%A6%AE%E0%A7%87%E0%A6%98%E0%A6%A8%E0%A6%BE_%E0%A6%97%E0%A7%8D%E0%A6%B0%E0%A7%81%E0%A6%AA_%E0%A6%85%E0%A6%AC_%E0%A6%87%E0%A6%A8%E0%A7%8D%E0%A6%A1%E0%A6%BE%E0%A6%B8%E0%A7%8D%E0%A6%9F%E0%A7%8D%E0%A6%B0%E0%A6%BF%E0%A6%9C"
]

def scrape_and_index(url):
    try:
        print(f"[PROCESS] {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
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
            if len(vectors) >= 50:
                vector_store.index.upsert(vectors=vectors)
                vectors = []

        if vectors:
            vector_store.index.upsert(vectors=vectors)
        print(f"[SUCCESS] Indexed {len(chunks)} chunks.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("\n--- Nexus Intelligence: Global Batch Ingestion Starting ---")
    for url in URLS:
        scrape_and_index(url)
    print("\n--- Batch Ingestion Complete ---")
