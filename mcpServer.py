import random

import requests
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("my-MCPServer")

@mcp.tool()
def Multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return (a * b) 

@mcp.tool()
def get_current_weather(city: str) -> str:
    print(f"[debug-server] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

if __name__ == "__main__":
    mcp.run(transport="sse")