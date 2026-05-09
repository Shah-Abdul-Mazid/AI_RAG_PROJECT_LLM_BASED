import os
from typing import List

def advanced_partition_file(file_path: str) -> List[str]:
    """
    Uses the Unstructured library for intelligent document partitioning.
    Handles PDFs with tables, images, and complex layouts.
    Falls back to basic text reading if unstructured is not installed.
    """
    print(f"[Loader] Partitioning: {os.path.basename(file_path)}")
    try:
        from unstructured.partition.auto import partition
        elements = partition(filename=file_path)
        chunks = []
        current_chunk = ""
        for el in elements:
            el_text = str(el).strip()
            if not el_text:
                continue
            if len(current_chunk) + len(el_text) < 1000:
                current_chunk += el_text + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = el_text + "\n"
        if current_chunk:
            chunks.append(current_chunk)
        print(f"[Loader] Unstructured partitioned into {len(chunks)} chunks.")
        return chunks if chunks else [""]
        
    except ImportError:
        print("[Loader] Unstructured not installed. Using basic text reader...")
        return _basic_text_read(file_path)
    except Exception as e:
        print(f"[Loader] Partition error: {e}. Falling back to basic reader.")
        return _basic_text_read(file_path)

def _basic_text_read(file_path: str) -> List[str]:
    """Fallback basic text reader for plain text, CSV, and simple files"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [text[i:i+1000] for i in range(0, len(text), 800)] if text else [""]
    except Exception as e:
        print(f"[Loader] Basic read failed: {e}")
        return [""]
