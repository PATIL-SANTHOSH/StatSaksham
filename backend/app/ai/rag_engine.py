import os
import re
import math
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pypdf import PdfReader
from pptx import Presentation
from app.ai.ollama_client import ollama_client

class RAGEngine:
    def __init__(self):
        pass

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract raw text from PDF, PPTX, TXT or DOCX files.
        """
        text = ""
        file_ext = file_type.lower().replace(".", "")

        try:
            if file_ext == "pdf":
                reader = PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text += f"\n--- Page {page_idx + 1} ---\n" + page_text

            elif file_ext in ["pptx", "ppt"]:
                prs = Presentation(file_path)
                for slide_idx, slide in enumerate(prs.slides):
                    slide_texts = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text.strip():
                            slide_texts.append(shape.text.strip())
                    if slide_texts:
                        text += f"\n--- Slide {slide_idx + 1} ---\n" + "\n".join(slide_texts)

            elif file_ext in ["txt", "md", "csv"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

            else:
                # Fallback binary reader
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

        except Exception as e:
            print(f"[RAGEngine] Error extracting text from {file_path}: {e}")
            text = f"Error extracting document text: {str(e)}"

        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Split text into overlapping semantic chunks.
        """
        if not text:
            return []

        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        lines = text.split('\n')
        
        chunks = []
        current_chunk = ""
        chunk_idx = 0

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if len(current_chunk) + len(line_str) <= chunk_size:
                current_chunk += (" " if current_chunk else "") + line_str
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk.strip(),
                        "token_count": len(current_chunk.split())
                    })
                    chunk_idx += 1
                    # Overlap
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                    current_chunk = overlap_text + " " + line_str
                else:
                    # Single line longer than chunk_size
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": line_str[:chunk_size],
                        "token_count": len(line_str[:chunk_size].split())
                    })
                    chunk_idx += 1
                    current_chunk = line_str[chunk_size - overlap:]

        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_idx,
                "content": current_chunk.strip(),
                "token_count": len(current_chunk.split())
            })

        return chunks

    def compute_embedding(self, text: str) -> List[float]:
        """
        Compute embedding using Ollama nomic-embed-text if available,
        or deterministic pseudo-embedding vector for fallback.
        """
        if ollama_client.is_available():
            emb = ollama_client.get_embedding(text)
            if emb:
                return emb

        # Deterministic lightweight 64-dim embedding based on character and term hashes
        vector = [0.0] * 64
        words = re.findall(r'\w+', text.lower())
        for w in words:
            h = hash(w) % 64
            vector[h] += 1.0
        # Normalize vector
        norm = math.sqrt(sum(x*x for x in vector)) or 1.0
        return [round(x / norm, 6) for x in vector]

    def similarity_search(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform cosine similarity search on chunk embeddings.
        """
        if not chunks:
            return []

        query_emb = self.compute_embedding(query)
        q_vec = np.array(query_emb, dtype=float)
        q_norm = np.linalg.norm(q_vec) or 1.0

        scored_chunks = []
        for c in chunks:
            emb = c.get("embedding")
            if not emb:
                emb = self.compute_embedding(c["content"])
            c_vec = np.array(emb, dtype=float)
            c_norm = np.linalg.norm(c_vec) or 1.0
            
            # Check dimensions match
            if len(q_vec) == len(c_vec):
                sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            else:
                # Text overlap score fallback
                q_words = set(query.lower().split())
                c_words = set(c["content"].lower().split())
                sim = len(q_words.intersection(c_words)) / max(1, len(q_words))

            scored_chunks.append((sim, c))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]

rag_engine = RAGEngine()
