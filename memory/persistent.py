"""Persistent Memory for J.A.R.V.I.S.

SQLite-based storage for user facts, preferences, and conversation history.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os


class PersistentMemory:
    """Persistent memory storage using SQLite.
    
    Stores:
    - User facts (name, preferences, etc.)
    - Conversation history (last N messages)
    - Long-term memory (important facts)
    """
    
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User facts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Long-term memory (important extracted facts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def set_fact(self, key: str, value: str, category: str = "general"):
        """Store a user fact.
        
        Args:
            key: Fact key (e.g., 'name', 'favorite_color')
            value: Fact value
            category: Fact category
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_facts (key, value, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, category))
            conn.commit()
    
    def get_fact(self, key: str) -> Optional[str]:
        """Get a user fact.
        
        Args:
            key: Fact key
            
        Returns:
            Fact value or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_facts WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_all_facts(self, category: Optional[str] = None) -> Dict[str, str]:
        """Get all user facts.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dict of facts
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT key, value FROM user_facts WHERE category = ?",
                    (category,)
                )
            else:
                cursor.execute("SELECT key, value FROM user_facts")
            return dict(cursor.fetchall())
    
    def add_conversation(self, role: str, content: str):
        """Add conversation message.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (role, content) VALUES (?, ?)",
                (role, content)
            )
            conn.commit()
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get recent conversation history.
        
        Args:
            limit: Number of messages to retrieve
            
        Returns:
            List of message dicts
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    
    def clear_conversations(self):
        """Clear all conversation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            conn.commit()
    
    def add_long_term_memory(self, fact: str, category: str = "general", importance: int = 5):
        """Add important fact to long-term memory.
        
        Args:
            fact: The fact to remember
            category: Fact category
            importance: Importance level (1-10)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO long_term_memory (fact, category, importance) VALUES (?, ?, ?)",
                (fact, category, importance)
            )
            conn.commit()
    
    def get_long_term_memory(self, category: Optional[str] = None, limit: int = 10) -> List[str]:
        """Get long-term memories.
        
        Args:
            category: Optional category filter
            limit: Maximum number of facts
            
        Returns:
            List of facts
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT fact FROM long_term_memory WHERE category = ? ORDER BY importance DESC LIMIT ?",
                    (category, limit)
                )
            else:
                cursor.execute(
                    "SELECT fact FROM long_term_memory ORDER BY importance DESC LIMIT ?",
                    (limit,)
                )
            return [row[0] for row in cursor.fetchall()]
    
    def clear_all(self):
        """Clear all memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_facts")
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM long_term_memory")
            conn.commit()
    
    def get_memory_summary(self) -> str:
        """Get summary of stored memory.
        
        Returns:
            Summary string
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM user_facts")
            facts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM long_term_memory")
            mem_count = cursor.fetchone()[0]
            
            return (
                f"Memory Stats:\n"
                f"  User Facts: {facts_count}\n"
                f"  Conversations: {conv_count}\n"
                f"  Long-term Memories: {mem_count}"
            )
