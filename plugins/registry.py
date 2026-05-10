"""Plugin Registry — auto-discovers and manages all plugins."""
import os
import importlib
import pkgutil
from typing import List, Optional, Type

from .base import BasePlugin


class PluginRegistry:
    """Registry that auto-discovers, loads, and routes to plugins.
    
    Usage:
        registry = PluginRegistry()
        registry.discover()  # Auto-find all plugins
        
        # In main loop:
        result = registry.process(text, jarvis_instance)
    """
    
    def __init__(self, jarvis_instance=None):
        self.jarvis = jarvis_instance
        self.plugins: List[BasePlugin] = []
        self._plugin_classes: List[Type[BasePlugin]] = []
    
    def discover(self, package_name: str = "plugins") -> int:
        """Auto-discover all plugins in the plugins package.
        
        Scans all modules in plugins/ directory, finds classes
        inheriting from BasePlugin, instantiates them.
        
        Returns:
            Number of plugins loaded
        """
        self.plugins = []
        self._plugin_classes = []
        
        # Get plugins directory path
        plugins_dir = os.path.join(os.path.dirname(__file__), "..")
        plugins_dir = os.path.abspath(plugins_dir)
        
        try:
            import plugins as plugins_pkg
            pkg_path = os.path.dirname(plugins_pkg.__file__)
            
            # Scan all modules in plugins package
            for importer, modname, ispkg in pkgutil.iter_modules([pkg_path]):
                # Skip __init__, base, registry
                if modname in ("__init__", "base", "registry"):
                    continue
                
                try:
                    module = importlib.import_module(f"plugins.{modname}")
                    
                    # Find plugin classes in module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr is not BasePlugin and
                            not getattr(attr, '__abstractmethods__', None)):
                            
                            self._plugin_classes.append(attr)
                            
                except Exception as e:
                    print(f"[Registry] Failed to load plugin module '{modname}': {e}")
                    
        except ImportError:
            print("[Registry] Could not import plugins package")
        
        # Instantiate plugins sorted by priority
        self._instantiate_plugins()
        
        print(f"[Registry] Loaded {len(self.plugins)} plugins")
        for p in self.plugins:
            print(f"  • {p.name} (priority={p.priority})")
        
        return len(self.plugins)
    
    def _instantiate_plugins(self):
        """Instantiate all discovered plugin classes sorted by priority."""
        # Sort by priority (lower = first)
        self._plugin_classes.sort(key=lambda c: getattr(c, 'priority', 100))
        
        for cls in self._plugin_classes:
            try:
                plugin = cls(jarvis_instance=self.jarvis)
                plugin.on_load()
                self.plugins.append(plugin)
            except Exception as e:
                print(f"[Registry] Failed to instantiate {cls.__name__}: {e}")
    
    def process(self, text: str) -> Optional[BasePlugin]:
        """Process text through all plugins.
        
        Iterates plugins by priority, returns first matching plugin.
        
        Args:
            text: User input text
            
        Returns:
            The plugin that handled the request, or None
        """
        lowered = text.lower().strip()
        
        for plugin in self.plugins:
            try:
                match = plugin.can_handle(lowered)
                if match is not None:
                    return plugin, match
            except Exception as e:
                print(f"[Registry] Error in {plugin.name}.can_handle: {e}")
        
        return None, None
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        for plugin in self.plugins:
            if plugin.name.lower() == name.lower():
                return plugin
        return None
    
    def get_plugins_info(self) -> List[dict]:
        """Get info about all loaded plugins."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "version": getattr(p, 'version', '1.0.0'),
                "priority": p.priority,
            }
            for p in self.plugins
        ]
    
    def reload(self):
        """Reload all plugins."""
        for plugin in self.plugins:
            plugin.on_unload()
        self.discover()
    
    def get_help_text(self) -> str:
        """Get combined help text from all plugins."""
        lines = ["📋 Доступные команды:", ""]
        for plugin in self.plugins:
            lines.append(f"• {plugin.get_help()}")
        return "\n".join(lines)
