"""Hybrid AI Router for J.A.R.V.I.S.

Routes requests between local (Ollama) and cloud (Hugging Face, OpenRouter) AI providers.
Uses a smart routing strategy based on request complexity and availability.
"""
import time
import requests
from typing import Dict, List, Optional, Tuple

from config import Config


class HybridRouter:
    """Smart router that chooses the best AI provider for each request.
    
    Strategy:
    - Simple/Local tasks -> Ollama (fast, private, offline)
    - Complex/Creative tasks -> OpenRouter (Llama 3.1 70B, GPT-4, etc.)
    - Fallback -> Hugging Face
    """
    
    def __init__(self):
        self.providers = {
            "ollama": {"available": False, "latency": float('inf'), "type": "local", "priority": 1},
            "openrouter": {"available": False, "latency": float('inf'), "type": "cloud", "priority": 3},
            "hf": {"available": False, "latency": float('inf'), "type": "cloud", "priority": 2},
        }
        self._check_providers()
    
    def _check_providers(self):
        """Check which providers are available."""
        # Check Ollama
        try:
            resp = requests.get(f"{Config.OLLAMA_URL}", timeout=2)
            if resp.status_code == 200:
                self.providers["ollama"]["available"] = True
                self.providers["ollama"]["latency"] = 50
        except:
            pass
        
        # Check OpenRouter (works without API key for free models)
        try:
            resp = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
            if resp.status_code == 200:
                self.providers["openrouter"]["available"] = True
                self.providers["openrouter"]["latency"] = 300
        except:
            pass
        
        # Check Hugging Face (has API key)
        if Config.HF_API_KEY:
            self.providers["hf"]["available"] = True
            self.providers["hf"]["latency"] = 200
        
        print(f"[HybridRouter] Providers: {self._get_status()}")
    
    def _get_status(self) -> Dict:
        """Get provider status."""
        return {
            name: {"available": info["available"], "type": info["type"]}
            for name, info in self.providers.items()
        }
    
    def route(self, message: str, history: List[Dict], require_tools: bool = False) -> Tuple[str, Dict]:
        """Route request to best provider."""
        has_internet = self._check_internet()
        
        # Priority: OpenRouter first (best models, no Chinese, understands context)
        # Fallback: Ollama (local) > HF (cloud)
        
        if has_internet and self.providers["openrouter"]["available"]:
            return "openrouter", self.providers["openrouter"]
        elif self.providers["ollama"]["available"]:
            return "ollama", self.providers["ollama"]
        elif has_internet and self.providers["hf"]["available"]:
            return "hf", self.providers["hf"]
        
        # Fallback to configured provider
        return Config.AI_PROVIDER, self.providers.get(Config.AI_PROVIDER, {})
    
    def _assess_complexity(self, message: str) -> str:
        """Assess request complexity."""
        lowered = message.lower()
        
        # Complex indicators
        complex_keywords = [
            "напиши", "создай", "код", "функция", "класс", "программа",
            "объясни", "почему", "как", "анализ", "сравни", "опиши",
            "github", "репозиторий", "коммит", "pull request",
            "переведи", "translation", "translate",
            "решение", "задача", "математика", "формула",
            "помоги", "помочь", "помощь",
        ]
        
        if any(kw in lowered for kw in complex_keywords):
            return "complex"
        
        # Simple indicators
        simple_keywords = [
            "привет", "пока", "спасибо", "время", "дата", "погода",
            "открой", "закрой", "включи", "выключи", "громче", "тише",
        ]
        
        if any(kw in lowered for kw in simple_keywords):
            return "simple"
        
        # Default to complex for safety
        return "complex"
    
    def _check_internet(self) -> bool:
        """Check if internet is available."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def get_fallback_chain(self) -> List[str]:
        """Get fallback chain of providers."""
        available = [
            name for name, info in self.providers.items()
            if info["available"]
        ]
        
        # Sort by priority (higher = better)
        available.sort(key=lambda x: self.providers[x]["priority"], reverse=True)
        
        return available
