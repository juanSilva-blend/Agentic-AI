from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# This command downloads and runs the official SQLite MCP server instantly
client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["mcp-server-sqlite", "--db-path", "./sales.db"] 
        )
    )
)

with client:
    agent = Agent(tools=client.list_tools_sync(), model="anthropic.claude-3-sonnet-20240229-v1:0")
    response = agent("Find the top 5 sales by amount (calculated as quantity * price). Please display the actual results to me as a Markdown table in your final response.")
    print(response)