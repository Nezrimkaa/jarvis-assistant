"""Simple Vector Memory for J.A.R.V.I.S.

Lightweight RAG implementation using numpy and cosine similarity.
No external vector DB required.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os


class VectorMemory:
    """Simple vector memory using sentence embeddings and cosine similarity.
    
    Stores text chunks as vectors and retrieves most similar ones.
    """
    
    def __init__(self, storage_path: str = "vector_memory.json"):
        self.storage_path = storage_path
        self.documents: List[str] = []
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict] = []
        self._load()
    
    def _simple_embed(self, text: str) -> np.ndarray:
        """Create simple embedding from text.
        
        Uses character n-gram frequency as a simple embedding.
        In production, use proper sentence transformers.
        
        Args:
            text: Input text
            
        Returns:
            Vector representation
        """
        # Simple bag-of-chars embedding (256 dim)
        text = text.lower()[:1000]  # Limit length
        vec = np.zeros(256, dtype=np.float32)
        
        for char in text:
            idx = ord(char) % 256
            vec[idx] += 1
        
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        
        return vec
    
    def add(self, text: str, metadata: Optional[Dict] = None):
        """Add document to vector memory.
        
        Args:
            text: Document text
            metadata: Optional metadata dict
        """
        vector = self._simple_embed(text)
        self.documents.append(text)
        self.vectors.append(vector)
        self.metadata.append(metadata or {})
        self._save()
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
        """Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of (text, similarity, metadata) tuples
        """
        if not self.vectors:
            return []
        
        query_vec = self._simple_embed(query)
        
        # Compute cosine similarities
        similarities = []
        for i, doc_vec in enumerate(self.vectors):
            sim = np.dot(query_vec, doc_vec)
            similarities.append((i, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k
        results = []
        for idx, sim in similarities[:top_k]:
            results.append((self.documents[idx], float(sim), self.metadata[idx]))
        
        return results
    
    def _save(self):
        """Save to disk."""
        data = {
            "documents": self.documents,
            "vectors": [v.tolist() for v in self.vectors],
            "metadata": self.metadata,
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """Load from disk."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.documents = data.get("documents", [])
            self.vectors = [np.array(v, dtype=np.float32) for v in data.get("vectors", [])]
            self.metadata = data.get("metadata", [])
        except Exception as e:
            print(f"[VectorMemory] Load error: {e}")
    
    def clear(self):
        """Clear all vectors."""
        self.documents = []
        self.vectors = []
        self.metadata = []
        self._save()
    
    def count(self) -> int:
        """Get document count."""
        return len(self.documents)
