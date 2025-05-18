import asyncio

from agents import Agent, Runner, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
import os

os.environ["OPENAI_API_KEY"]='Your OpenAI API key goes here'

async def runAgent(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use the `add` tool to add two numbers
    message = "Multiply these numbers: 7 and 22."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Final Output: {result.final_output}")

    # Run the `get_weather` tool
    message = "What's the weather in Cobourg?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"Final Output: {result.final_output}")

async def defineMCPServerandRunAgent():
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        
        with trace(workflow_name="mcpClientA"):

            tools = await server.list_tools()
            # Print the description of each available tool
            print("\n Available tools:")
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            await runAgent(server)

    async with MCPServerSse(
    name="SSE Python Server",
    params={
        "url": "http://localhost:8000/sse",
        },
    ) as server1:
        
        with trace(workflow_name="mcpClientB"):

            tools = await server1.list_tools()
            # Print the description of each available tool
            print("\n Available tools:")
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            await runAgent(server1)
        

if __name__ == "__main__":
    
    async def main():
        await defineMCPServerandRunAgent()

    asyncio.run(main())


