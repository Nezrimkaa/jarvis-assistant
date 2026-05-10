"""Tool Manager for J.A.R.V.I.S.

Manages function calling / tool use for LLMs.
Converts plugins to JSON Schema and executes tool calls.
"""
import json
from typing import Dict, List, Optional, Any

from plugins import PluginRegistry


class ToolManager:
    """Manages tool definitions and execution for LLM function calling.
    
    Each plugin can expose itself as a tool with JSON Schema.
    The LLM can then decide which tool to call.
    """
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.tools = self._build_tools()
    
    def _build_tools(self) -> List[Dict]:
        """Build tool definitions from plugins.
        
        Returns:
            List of OpenAI-compatible tool definitions
        """
        tools = []
        
        for plugin in self.registry.plugins:
            # Build parameters schema from triggers
            params = self._extract_params(plugin)
            
            tool = {
                "type": "function",
                "function": {
                    "name": plugin.name,
                    "description": plugin.description,
                    "parameters": {
                        "type": "object",
                        "properties": params["properties"],
                        "required": params["required"],
                    },
                },
            }
            tools.append(tool)
        
        return tools
    
    def _extract_params(self, plugin) -> Dict:
        """Extract parameters from plugin triggers.
        
        Returns:
            Dict with 'properties' and 'required' keys
        """
        properties = {}
        required = []
        
        # Extract from first trigger that has capture groups
        for trigger in plugin.triggers:
            if isinstance(trigger, tuple) and len(trigger) == 2:
                pattern, handler = trigger
                # Check if pattern has capture groups
                if "(" in pattern and ")" in pattern:
                    # Add a generic 'query' parameter
                    properties["query"] = {
                        "type": "string",
                        "description": f"Query or parameter for {plugin.name}",
                    }
                    required.append("query")
                    break
        
        return {
            "properties": properties,
            "required": required,
        }
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute a tool by name.
        
        Args:
            tool_name: Name of the plugin/tool
            arguments: Arguments from LLM
            
        Returns:
            Tool execution result
        """
        plugin = self.registry.get_plugin(tool_name)
        
        if not plugin:
            return f"[ERROR] Tool '{tool_name}' not found"
        
        try:
            # Build text from arguments
            if "query" in arguments:
                text = f"{tool_name} {arguments['query']}"
            else:
                text = tool_name
            
            # Check if plugin can handle
            match = plugin.can_handle(text.lower())
            if match:
                result = plugin.execute(text, match)
                if result.success:
                    return result.response
                else:
                    return f"[ERROR] Tool execution failed"
            else:
                # Try direct execution
                result = plugin.execute(text)
                if result.success:
                    return result.response
                else:
                    return f"[ERROR] Tool '{tool_name}' rejected the request"
                    
        except Exception as e:
            return f"[ERROR] Tool execution error: {e}"
    
    def get_tools_json(self) -> str:
        """Get tools as JSON string.
        
        Returns:
            JSON string of tool definitions
        """
        return json.dumps(self.tools, ensure_ascii=False, indent=2)
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return [tool["function"]["name"] for tool in self.tools]
