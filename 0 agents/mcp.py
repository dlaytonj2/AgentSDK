from typing import Any, Dict, Optional


class MCPServer:
    """Base class for MCP servers."""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        self.name = name
        self.params = params or {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MCPServerSse(MCPServer):
    """MCP server implementation using Server-Sent Events (SSE)."""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.url = params.get("url") if params else None
        
    async def __aenter__(self):
        # Initialize connection to the SSE server
        print(f"Connecting to SSE server at {self.url}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close connection to the SSE server
        print(f"Disconnecting from SSE server at {self.url}") 