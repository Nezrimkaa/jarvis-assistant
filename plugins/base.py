"""Base Plugin class for J.A.R.V.I.S. plugin architecture."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Pattern
import re


@dataclass
class PluginResult:
    """Result of plugin execution."""
    success: bool
    response: str = ""
    should_speak: bool = True
    add_to_history: bool = True


class BasePlugin(ABC):
    """Abstract base class for all J.A.R.V.I.S. plugins.
    
    Each plugin handles a specific domain of commands.
    The registry calls can_handle() first, then execute().
    """
    
    # Plugin metadata
    name: str = "unnamed"
    description: str = ""
    version: str = "1.0.0"
    
    # Matching priority (lower = higher priority, checked first)
    priority: int = 100
    
    # Trigger patterns (regex strings or callable predicates)
    # Format: [(pattern, handler_name), ...]
    triggers: List = []
    
    def __init__(self, jarvis_instance=None):
        """Initialize plugin.
        
        Args:
            jarvis_instance: Reference to the main Jarvis class
        """
        self.jarvis = jarvis_instance
        self._compiled_triggers: List = []
        self._compile_triggers()
    
    def _compile_triggers(self):
        """Compile regex triggers for faster matching."""
        self._compiled_triggers = []
        for trigger in self.triggers:
            if isinstance(trigger, tuple) and len(trigger) == 2:
                pattern, handler_name = trigger
                if isinstance(pattern, str):
                    try:
                        compiled = re.compile(pattern, re.IGNORECASE | re.UNICODE)
                        self._compiled_triggers.append((compiled, handler_name))
                    except re.error as e:
                        print(f"[Plugin:{self.name}] Invalid regex: {pattern} - {e}")
            elif isinstance(trigger, str):
                # Simple keyword trigger
                try:
                    compiled = re.compile(trigger, re.IGNORECASE | re.UNICODE)
                    self._compiled_triggers.append((compiled, "execute"))
                except re.error as e:
                    print(f"[Plugin:{self.name}] Invalid regex: {trigger} - {e}")
    
    def can_handle(self, text: str) -> Optional[re.Match]:
        """Check if this plugin can handle the given text.
        
        Args:
            text: Normalized user input (already lowercased)
            
        Returns:
            Match object if can handle, None otherwise
        """
        for compiled_pattern, handler_name in self._compiled_triggers:
            match = compiled_pattern.search(text)
            if match:
                return match
        return None
    
    @abstractmethod
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Execute the plugin's main action.
        
        Args:
            text: Full user input
            match: Regex match object if triggered by pattern
            
        Returns:
            PluginResult with response and metadata
        """
        pass
    
    def on_load(self):
        """Called when plugin is loaded into registry.
        Override to perform initialization."""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded.
        Override to cleanup resources."""
        pass
    
    def get_help(self) -> str:
        """Return help text for this plugin."""
        return f"**{self.name}**: {self.description}"
    
    def _get_commands(self):
        """Get reference to SystemCommands if available."""
        if self.jarvis and hasattr(self.jarvis, 'commands'):
            return self.jarvis.commands
        return None
    
    def _get_brain(self):
        """Get reference to Brain if available."""
        if self.jarvis and hasattr(self.jarvis, 'brain'):
            return self.jarvis.brain
        return None
    
    def _get_voice(self):
        """Get reference to Voice if available."""
        if self.jarvis and hasattr(self.jarvis, 'voice'):
            return self.jarvis.voice
        return None
    
    def _get_history(self):
        """Get conversation history."""
        if self.jarvis and hasattr(self.jarvis, 'history'):
            return self.jarvis.history
        return []
