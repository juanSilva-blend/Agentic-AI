from strands import Agent,tool
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from mcp import stdio_client, StdioServerParameters
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import json

MODEL="qwen.qwen3-next-80b-a3b"

bedrock_model = BedrockModel(
            model_id=MODEL,
            temperature=0.3,
            top_p=0.8,
                        
        )

SYSTEM_PROMPT = """You are an expert data analyst. Use the tools at your disposal to answer the user's questions. 
In the sales database there's only one table called sales. 
When providing tabular data, format it as a Markdown table for better readability. 
Always include the actual results in your final response. 
NEVER create dummy data to show, always look for actual data in the database. 
NEVER create, change or delete rows, tables or directories without explicit permission of the request. 
for graphs you can use the create_bar_chart, create_line_chart and create_pie_chart tools and they will do all the work, use snake case for these files and .png.
If not specified to create a graph or save the results in a csv, create a graph you see fit to showcase the data.
if you want to quote a graph, don't use markdown, just mention the filename of the graph saved in the ./src/output/graphs folder.
YOUR JOB IS CRITICAL, FOLLOW THE INSTRUCTIONS TO THE LETTER AND PROVIDE THE MOST ACCURATE DATA ANALYSIS POSSIBLE.
"""

@tool
def create_bar_chart(data: str, x_column: str, y_column: str, title: str, filename: str) -> str:
    """
    Create a bar chart from data and save it as an image.
    
    Args:
        data: JSON string of the data (list of dictionaries)
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Chart title
        filename: Output filename (e.g., 'chart.png')
    """
    df = pd.DataFrame(json.loads(data))
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_column], df[y_column])
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'./src/output/graphs/{filename}')
    plt.close()
    return f"Chart saved as {filename}"

@tool
def create_line_chart(data: str, x_column: str, y_column: str, title: str, filename: str) -> str:
    """
    Create a line chart from data and save it as an image.
    
    Args:
        data: JSON string of the data (list of dictionaries)
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Chart title
        filename: Output filename (e.g., 'chart.png')
    """
    df = pd.DataFrame(json.loads(data))
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_column], df[y_column], marker='o')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'./src/output/graphs/{filename}')
    plt.close()
    return f"Chart saved as {filename}"

@tool
def create_pie_chart(data: str, labels_column: str, values_column: str, title: str, filename: str) -> str:
    """
    Create a pie chart from data and save it as an image.
    
    Args:
        data: JSON string of the data (list of dictionaries)
        labels_column: Column name for labels
        values_column: Column name for values
        title: Chart title
        filename: Output filename (e.g., 'chart.png')
    """
    df = pd.DataFrame(json.loads(data))
    plt.figure(figsize=(10, 8))
    values = pd.to_numeric(df[values_column], errors='coerce').fillna(0)
    labels = df[labels_column].astype(str).tolist()
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f'./src/output/graphs/{filename}')
    plt.close()
    return f"Chart saved as {filename}"

sqlite_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["mcp-server-sqlite", "--db-path", "./sales.db"] 
        )
    )
)

fs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="npx",
            args=[
                "-y", 
                "@modelcontextprotocol/server-filesystem", 
                "./src/output/csv_files"
            ]
        )
    ),
    startup_timeout=120
)

def get_agent_response(prompt: str) -> str:
    """Get response from the sales agent"""
    with sqlite_client, fs_client:
        agent = Agent(
            tools=sqlite_client.list_tools_sync() + fs_client.list_tools_sync() + [create_bar_chart, create_line_chart, create_pie_chart],
            model=bedrock_model,
        )
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser request: {prompt}"
        response = agent(full_prompt)
        return str(response)

async def get_agent_response_async(prompt: str) -> str:
    """Get response from the sales agent asynchronously"""
    with sqlite_client, fs_client:
        agent = Agent(
            tools=sqlite_client.list_tools_sync() + fs_client.list_tools_sync() + [create_bar_chart, create_line_chart, create_pie_chart],
            model=bedrock_model,
        )
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser request: {prompt}"
        result = await agent.invoke_async(full_prompt)
        return str(result)

# Run directly if executed as script
if __name__ == "__main__":
    prompt = "Quién fue el vendedor con más ventas en Bogotá. Genera un grafico circular para mostrar los datos"
    response = get_agent_response(prompt)
    print(response)