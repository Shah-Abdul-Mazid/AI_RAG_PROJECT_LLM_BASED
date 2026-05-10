import os
from typing import List

def advanced_partition_file(file_path: str) -> List[str]:
    """
    Uses Unstructured for advanced parsing. 
    Falls back to pypdf for reliability if Unstructured fails.
    """
    print(f"[Loader] Partitioning: {os.path.basename(file_path)}")
    
    # 1. Try Unstructured (Advanced)
    try:
        from unstructured.partition.auto import partition
        elements = partition(filename=file_path)
        chunks = []
        current_chunk = ""
        for el in elements:
            el_text = str(el).strip()
            if not el_text: continue
            if len(current_chunk) + len(el_text) < 1000:
                current_chunk += el_text + "\n"
            else:
                if current_chunk: chunks.append(current_chunk)
                current_chunk = el_text + "\n"
        if current_chunk: chunks.append(current_chunk)
        
        # If it worked, return the chunks
        if chunks and len(chunks[0]) > 10:
            print(f"[Loader] Unstructured success: {len(chunks)} chunks.")
            return chunks
    except Exception as e:
        print(f"[Loader] Unstructured skipped: {e}")

    # 2. Try PyPDF (Reliable Fallback for AWS)
    if file_path.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            print("[Loader] Using PyPDF fallback...")
            reader = PdfReader(file_path)
            full_text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    full_text += extracted + "\n"
            
            if full_text.strip():
                # Split into chunks of 1000 chars
                return [full_text[i:i+1000] for i in range(0, len(full_text), 800)]
        except Exception as e:
            print(f"[Loader] PyPDF failed: {e}")

    # 3. Last Resort: Basic Text Read
    return _basic_text_read(file_path)

def _basic_text_read(file_path: str) -> List[str]:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        if text.strip():
            return [text[i:i+1000] for i in range(0, len(text), 800)]
        return [""]
    except Exception:
        return [""]
