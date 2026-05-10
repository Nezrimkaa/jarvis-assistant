"""Plugin System for J.A.R.V.I.S.

Architecture:
    - BasePlugin: abstract base for all plugins
    - PluginRegistry: auto-discovers and manages plugins
    - Each plugin file defines one or more plugin classes
"""
from .base import BasePlugin, PluginResult
from .registry import PluginRegistry

__all__ = ["BasePlugin", "PluginResult", "PluginRegistry"]
