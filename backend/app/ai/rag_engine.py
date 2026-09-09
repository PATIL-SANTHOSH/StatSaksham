import os
import re
import math
from typing import List, Dict, Any, Optional
import numpy as np
from app.ai.ollama_client import ollama_client
from app.ai.document_extractor import document_extractor, clean_text

class RAGEngine:
    def __init__(self):
        pass

    def extract_document(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """
        Extract structured page/slide text blocks using the DocumentExtractor.
        Returns: List[{"page": int, "text": str, "source": str, "type": str}]
        """
        return document_extractor.extract_document_pages(file_path, filename)

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Backward-compatible helper returning unified text.
        """
        filename = os.path.basename(file_path)
        try:
            pages = self.extract_document(file_path, filename)
            blocks = []
            for p in pages:
                label = f"--- Page {p['page']} ---" if p.get('type') == 'page' else f"--- Slide {p['page']} ---"
                blocks.append(f"\n{label}\n{p['text']}")
            return clean_text("\n".join(blocks))
        except Exception as e:
            print(f"[RAGEngine] Error extracting text from {file_path}: {e}")
            return f"Error extracting document text: {str(e)}"

    def chunk_document_pages(
        self, 
        pages: List[Dict[str, Any]], 
        chunk_size_words: int = 180, 
        overlap_words: int = 35
    ) -> List[Dict[str, Any]]:
        """
        Chunk structured page blocks while preserving page/slide numbering.
        """
        if not pages:
            return []

        chunks = []
        chunk_idx = 0

        for p in pages:
            page_num = p.get("page", 1)
            source_name = p.get("source", "document")
            page_type = p.get("type", "page")
            text = clean_text(p.get("text", ""))
            
            if not text:
                continue

            words = text.split()
            if len(words) <= chunk_size_words:
                # Single chunk for this page
                chunks.append({
                    "chunk_index": chunk_idx,
                    "page": page_num,
                    "type": page_type,
                    "source": source_name,
                    "content": text,
                    "token_count": len(words)
                })
                chunk_idx += 1
            else:
                # Split with overlap
                step = max(1, chunk_size_words - overlap_words)
                for start_idx in range(0, len(words), step):
                    chunk_words = words[start_idx:start_idx + chunk_size_words]
                    chunk_str = " ".join(chunk_words)
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page": page_num,
                        "type": page_type,
                        "source": source_name,
                        "content": chunk_str,
                        "token_count": len(chunk_words)
                    })
                    chunk_idx += 1
                    if start_idx + chunk_size_words >= len(words):
                        break

        return chunks

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
        """
        Standard chunking fallback for raw text input.
        """
        if not text or not text.strip():
            return []

        cleaned = clean_text(text)
        words = cleaned.split()
        chunk_size_words = max(50, chunk_size // 5)
        overlap_words = max(10, overlap // 5)
        step = max(1, chunk_size_words - overlap_words)
        
        chunks = []
        chunk_idx = 0
        for start_idx in range(0, len(words), step):
            chunk_words = words[start_idx:start_idx + chunk_size_words]
            chunks.append({
                "chunk_index": chunk_idx,
                "page": 1,
                "type": "page",
                "source": "manual_text",
                "content": " ".join(chunk_words),
                "token_count": len(chunk_words)
            })
            chunk_idx += 1
            if start_idx + chunk_size_words >= len(words):
                break

        return chunks

    def compute_embedding(self, text: str) -> List[float]:
        """
        Compute embedding using Ollama nomic-embed-text (768-dim),
        or deterministic 64-dim normalized term-frequency fallback vector if Ollama is offline.
        """
        if ollama_client.is_available():
            emb = ollama_client.get_embedding(text)
            if emb and len(emb) > 0:
                return emb

        # Deterministic 64-dim normalized term-frequency vector fallback
        vector = [0.0] * 64
        words = re.findall(r'\w+', text.lower())
        for w in words:
            h = hash(w) % 64
            vector[h] += 1.0
        norm = math.sqrt(sum(x*x for x in vector)) or 1.0
        return [round(x / norm, 6) for x in vector]

    def similarity_search(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]], 
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Perform fast cosine similarity vector search over candidate chunks.
        """
        if not chunks:
            return []

        query_emb = self.compute_embedding(query)
        q_vec = np.array(query_emb, dtype=float)
        q_norm = np.linalg.norm(q_vec) or 1.0

        scored_chunks = []
        for c in chunks:
            emb = c.get("embedding") or c.get("embedding_json")
            if not emb:
                emb = self.compute_embedding(c.get("content", ""))
            
            c_vec = np.array(emb, dtype=float)
            c_norm = np.linalg.norm(c_vec) or 1.0

            if len(q_vec) == len(c_vec):
                sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            else:
                # Fallback term overlap if dimensions differ
                q_words = set(query.lower().split())
                c_words = set(c.get("content", "").lower().split())
                sim = len(q_words.intersection(c_words)) / max(1, len(q_words))

            # Clone chunk dict and attach score
            chunk_copy = dict(c)
            chunk_copy["similarity_score"] = round(sim, 4)
            scored_chunks.append((sim, chunk_copy))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]

rag_engine = RAGEngine()
