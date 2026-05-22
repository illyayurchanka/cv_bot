from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional
from datetime import datetime

TOOLS = {}

def tool(name: str, description: str, parameters: dict, model: type[BaseModel]):
    """Decorator  to register a function as an agent tool."""
    def decorator(func):
        TOOLS[name] = {
                "function": func,
                "model": model,
                "schema": {
					"type": "function",
					"function": {
						"name": name,
						"description": description,
						"parameters": {
							"type": "object",
							"properties": parameters,
							"required": list(parameters.keys())
						}
					}
            	}
        	}
        return func
    return decorator

def execute_tool(name: str, arguments: dict) -> str:
    """Execute a registered tool by name."""
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        func = TOOLS[name]["function"]
        return func(**arguments)
    except Exception as e:
        return f"Tool errror ({name}): {e}"


def get_tool_schemas() -> list:
    """Get all tool schemas for the api call."""
    return [t["schema"] for t in TOOLS.values()]
