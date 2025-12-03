from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

# --- Configuración de Rutas ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sales.db")
OUTPUT_GRAPHS = os.path.join(BASE_DIR, "src", "output", "graphs")
OUTPUT_CSV = os.path.join(BASE_DIR, "src", "output", "csv_files")

os.makedirs(OUTPUT_GRAPHS, exist_ok=True)
os.makedirs(OUTPUT_CSV, exist_ok=True)

# --- Herramientas (Tools) ---

@tool
def create_bar_chart(data: str, x_column: str, y_column: str, title: str, filename: str) -> str:
    """Create a bar chart from JSON data and save it as an image."""
    try:
        df = pd.DataFrame(json.loads(data))
        plt.figure(figsize=(10, 6))
        plt.bar(df[x_column], df[y_column], color='skyblue')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        save_path = os.path.join(OUTPUT_GRAPHS, filename)
        plt.savefig(save_path)
        plt.close()
        return f"Chart saved successfully at: {filename}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"

@tool
def create_line_chart(data: str, x_column: str, y_column: str, title: str, filename: str) -> str:
    """Create a line chart from JSON data and save it as an image."""
    try:
        df = pd.DataFrame(json.loads(data))
        plt.figure(figsize=(10, 6))
        plt.plot(df[x_column], df[y_column], marker='o')
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True)
        plt.tight_layout()
        
        save_path = os.path.join(OUTPUT_GRAPHS, filename)
        plt.savefig(save_path)
        plt.close()
        return f"Chart saved successfully at: {filename}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"

@tool
def create_pie_chart(data: str, labels_column: str, values_column: str, title: str, filename: str) -> str:
    """Create a pie chart from JSON data and save it as an image."""
    try:
        df = pd.DataFrame(json.loads(data))
        plt.figure(figsize=(10, 8))
        values = pd.to_numeric(df[values_column], errors='coerce').fillna(0)
        labels = df[labels_column].astype(str).tolist()
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title(title)
        plt.tight_layout()
        
        save_path = os.path.join(OUTPUT_GRAPHS, filename)
        plt.savefig(save_path)
        plt.close()
        return f"Chart saved successfully at: {filename}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"

# --- Función Principal del Agente ---

def query_sales_agent(user_query: str):
    """
    Inicializa los clientes MCP y ejecuta el agente para una consulta específica.
    """
    # 1. Configurar Cliente SQLite
    sqlite_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx", 
                args=["mcp-server-sqlite", "--db-path", DB_PATH] 
            )
        )
    )

    # 2. Configurar Cliente Filesystem
    fs_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=[
                    "-y", 
                    "@modelcontextprotocol/server-filesystem", 
                    OUTPUT_CSV 
                ]
            )
        ),
        startup_timeout=120
    )

    try:
        with sqlite_client, fs_client:
            # Corrección de indentación aquí:
            all_tools = (
                sqlite_client.list_tools_sync() + 
                fs_client.list_tools_sync() + 
                [create_bar_chart, create_line_chart, create_pie_chart]
            )
            
            # Inicializar Agente
            # IMPORTANTE: Cambia "model" si usas otra API Key
            agent = Agent(
                tools=all_tools, 
                model="qwen.qwen3-next-80b-a3b" 
            )

            system_prompt = (
                "You are an expert data analyst. "
                "1. Always check the database schema first using sqlite tools. "
                "2. When creating charts, use the specific chart tools provided. "
                "3. If asked to save data, use the filesystem write tools to save CSVs. "
                "4. Format tabular answers in Markdown. "
                f"User Request: {user_query}"
            )
            
            response = agent(system_prompt)
            return response.text

    except Exception as e:
        return f"❌ Error en el agente: {str(e)}"