"""Memory Manager for J.A.R.V.I.S.

Combines persistent (SQLite) and vector memory for RAG.
"""
from typing import List, Dict, Optional

from memory.persistent import PersistentMemory
from memory.vector import VectorMemory


class MemoryManager:
    """Unified memory manager.
    
    Provides:
    - Persistent facts and history (SQLite)
    - Vector search for RAG (numpy)
    """
    
    def __init__(self):
        self.persistent = PersistentMemory()
        self.vector = VectorMemory()
    
    def remember_fact(self, key: str, value: str, category: str = "general"):
        """Remember a user fact.
        
        Args:
            key: Fact key
            value: Fact value
            category: Fact category
        """
        self.persistent.set_fact(key, value, category)
    
    def recall_fact(self, key: str) -> Optional[str]:
        """Recall a user fact.
        
        Args:
            key: Fact key
            
        Returns:
            Fact value or None
        """
        return self.persistent.get_fact(key)
    
    def add_to_history(self, role: str, content: str):
        """Add to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        self.persistent.add_conversation(role, content)
    
    def get_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get conversation history.
        
        Args:
            limit: Number of messages
            
        Returns:
            List of message dicts
        """
        return self.persistent.get_conversation_history(limit)
    
    def add_knowledge(self, text: str, metadata: Optional[Dict] = None):
        """Add knowledge to vector memory.
        
        Args:
            text: Knowledge text
            metadata: Optional metadata
        """
        self.vector.add(text, metadata)
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[str]:
        """Search knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant texts
        """
        results = self.vector.search(query, top_k)
        return [text for text, sim, meta in results]
    
    def get_context_for_llm(self, message: str) -> str:
        """Build context string for LLM.
        
        Includes relevant facts and knowledge.
        
        Args:
            message: Current user message
            
        Returns:
            Context string for LLM prompt
        """
        context_parts = []
        
        # Add user facts
        facts = self.persistent.get_all_facts()
        if facts:
            facts_str = ", ".join([f"{k}={v}" for k, v in facts.items()])
            context_parts.append(f"User facts: {facts_str}")
        
        # Add relevant knowledge
        knowledge = self.search_knowledge(message, top_k=2)
        if knowledge:
            context_parts.append("Relevant knowledge:")
            for k in knowledge:
                context_parts.append(f"  - {k}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def clear_all(self):
        """Clear all memory."""
        self.persistent.clear_all()
        self.vector.clear()
    
    def get_stats(self) -> str:
        """Get memory statistics."""
        return (
            f"{self.persistent.get_memory_summary()}\n"
            f"  Vector Documents: {self.vector.count()}"
        )
