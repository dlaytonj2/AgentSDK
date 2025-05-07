"""Agent implementation for AI interactions."""
from typing import Any, List, Optional

from .mcp import MCPServer
from .model_settings import ModelSettings


class Agent:
    """Agent class for interacting with AI backends."""
    
    def __init__(
        self,
        name: str,
        instructions: str,
        mcp_servers: Optional[List[MCPServer]] = None,
        model_settings: Optional[ModelSettings] = None,
        model: str = "gpt-4o",
        tools: List[Any] = None,
        output_type: Any = None,
    ):
        self.name = name
        self.instructions = instructions
        self.mcp_servers = mcp_servers or []
        self.model_settings = model_settings
        self.model = model
        self.tools = tools or []
        self.output_type = output_type 