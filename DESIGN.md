# 🏗️ Agentic-AI: Design Process Documentation

## 1. Project Overview

**Project Name:** Agentic-AI - Sales Analysis Agent  
**Objective:** Build an intelligent agent that analyzes sales data using natural language, generates SQL queries, and produces visualizations or reports.  
**Technology Stack:** LangGraph/Strands Agents, SQLite, MCP (Model Context Protocol), Streamlit

---

## 2. Architecture Overview

### High-Level Design Pattern

```
User Query (Natural Language)
    ↓
[Streamlit UI / Frontend]
    ↓
[Agent Orchestrator - Strands Agent]
    ├─→ SQL Generation Tool
    ├─→ MCP SQLite Client
    ├─→ Chart Generation Tools
    └─→ CSV Export Tools
    ↓
[SQLite Database]
    ↓
[Visualization & Export]
    ↓
Results to User
```

---

## 3. Component Design

### 3.1 Data Layer

**File:** `database/DB.py`

**Purpose:** Initialize SQLite database from CSV data

**Design Decisions:**
- Use **SQLite** for simplicity and portability
- Load data from `sales.csv` using **Pandas**
- Use **SQLAlchemy** as ORM for database operations
- Table schema: `sales(id, vendedor, sede, producto, cantidad, precio, fecha)`

**Key Features:**
```python
- Read CSV → Pandas DataFrame
- Transform DataFrame → SQLite table
- Enable complex queries without external services
```

---

### 3.2 Agent Layer

**File:** `src/agent/sqlite_agent.py`

**Architecture:** Multi-tool agent with MCP clients

#### Tools Implemented:

1. **Chart Generation Tools**
   - `create_bar_chart()`: Generate bar charts
   - `create_line_chart()`: Generate line charts
   - `create_pie_chart()`: Generate pie charts
   - **Output Location:** `src/output/graphs/`

2. **MCP Clients**
   - **SQLite Client:** Execute SQL queries via MCP protocol
     - Server: `mcp-server-sqlite`
     - Database: `sales.db`
   
   - **Filesystem Client:** Write/read files
     - Server: `@modelcontextprotocol/server-filesystem`
     - Allowed Path: `src/output/csv_files/`

#### Design Patterns:

**Tool Decorator Pattern:**
```python
@tool
def create_bar_chart(data: str, x_column: str, y_column: str, title: str, filename: str) -> str:
    # Enables agent to discover and invoke tools
```

**MCP Client Pattern:**
```python
sqlite_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(...))
)
```

---

### 3.3 Presentation Layer

**File:** `src/main.py`

**Framework:** Streamlit

**Design Purpose:**
- User-friendly web interface
- Accepts natural language queries
- Displays results (tables, charts, exports)

**Planned Features:**
- Query input box
- Result display (multiple formats)
- Chart visualization
- CSV download capability

**Status (Recent):**
- A Streamlit-based UI was implemented at `src/main.py` with tabs for Analysis, Data Explorer, Visualizations and Help. The repository includes a `run.sh` helper that detects the project virtualenv and runs Streamlit via `python -m streamlit`.
- Note: importing the agent currently triggers MCP clients at import-time (see Operational Notes). See recommendations below to avoid import-time side effects.

---

## 4. Data Flow Design

### Query Processing Pipeline

```
[1. User Input]
        ↓ (Natural Language Query)
[2. Agent Interpretation]
        ↓ (Strands Agent analyzes query intent)
[3. Tool Selection]
        ├─ SQL Generation?
        ├─ Visualization?
        └─ File Export?
        ↓
[4. Execution]
        ├─ SQLite MCP → Executes SQL Query
        ├─ Chart Tool → Generates visualization
        └─ Filesystem MCP → Exports to CSV
        ↓
[5. Result Aggregation]
        ↓ (Combine results from multiple tools)
[6. User Output]
        ├─ Display Data
        ├─ Show Charts
        └─ Provide Download Links
```

---

## 5. Tool Design Specifications

### 5.1 Chart Generation Tools

**Design Decision:** Use Matplotlib with file-based output

**Advantages:**
- No server-side rendering overhead
- Works in any environment (server/local)
- Supports static images for archiving
- Compatible with multiple visualization formats

**Implementation Details:**
```python
Flow:
1. Parse JSON data string
2. Convert to Pandas DataFrame
3. Create matplotlib figure
4. Apply styling (labels, title, rotation)
5. Save to disk
6. Return confirmation message
```

---

### 5.2 Database Interaction (MCP SQLite)

**MCP Integration Design:**

**Advantages of MCP Approach:**
- Standardized protocol for external integrations
- Security: Restricted database access
- Composability: Can chain multiple MCP servers
- Decoupling: Agent doesn't directly access DB

**Configuration:**
```python
MCPClient(
    stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["mcp-server-sqlite", "--db-path", "./sales.db"]
        )
    )
)
```

**Operational Note (runtime issues observed):**
- On some systems the repository may not have the `uvx` executable available in PATH, which causes the MCP client initialization to fail during import (FileNotFoundError for `uvx`). This project reproduced that error when starting Streamlit because `src/agent/sqlite_agent.py` starts MCP clients during module import.

**Workarounds & Recommendations:**
- Install `uvx` globally via npm (requires Node.js):
  ```bash
  sudo npm install -g @modelcontextprotocol/uvx || sudo npm install -g uvx
  ```
- Use `npx` to invoke the MCP server without a global install, e.g. set `command='npx'` and `args=['-y','@modelcontextprotocol/mcp-server-sqlite','--db-path','./sales.db']`.
- Better: refactor the agent to lazily initialize MCP clients (avoid `with sqlite_client, fs_client:` at import-time). Provide a `get_agent()` factory that starts clients on-demand and handles errors cleanly.

These changes improve robustness in developer environments and CI where global npm packages are not guaranteed.

---

### 5.3 File System Access (MCP Filesystem)

**Design Purpose:** Secure file operations

**Security Design:**
- Restrict access to `src/output/csv_files/` directory
- Prevent directory traversal attacks
- Control read/write operations through MCP

**Use Cases:**
- Export query results to CSV
- Read previously generated reports
- Store long-term analysis outputs

---

## 6. Query Processing Logic

### Example: "Top 5 productos más vendidos en Medellín"

```
Agent Decision Flow:
┌─────────────────────────────────────┐
│ User Query (Natural Language)       │
│ "Top 5 productos en Medellín"       │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Agent Intent Detection              │
│ - Extract: Location (Medellín)      │
│ - Extract: Metric (productos)       │
│ - Extract: Limit (Top 5)            │
│ - Detect Output: Visualization      │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ SQL Generation by Agent             │
│ SELECT producto, SUM(cantidad)      │
│ FROM sales                          │
│ WHERE sede='Medellín'               │
│ GROUP BY producto                   │
│ ORDER BY SUM(cantidad) DESC         │
│ LIMIT 5;                            │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Execute via SQLite MCP              │
│ Database Query Execution            │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Chart Generation                    │
│ Tool: create_bar_chart()            │
│ X-axis: producto                    │
│ Y-axis: total_vendido               │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Output Delivery                     │
│ ✓ Table Display                     │
│ ✓ Chart Image                       │
│ ✓ Summary Statistics                │
└─────────────────────────────────────┘
```

---

## 7. Directory Structure & Responsibilities

```
Agentic-AI/
│
├── database/
│   ├── DB.py              # Database initialization & schema
│   └── callingDB.py       # CRUD operations (reference)
│
├── src/
│   ├── main.py            # Streamlit UI & entry point
│   ├── example.py         # Reference implementation
│   │
│   ├── agent/
│   │   └── sqlite_agent.py     # Agent tools & MCP clients
│   │
│   └── output/
│       ├── csv_files/          # Exported data (CSV)
│       └── graphs/             # Generated visualizations
│
├── sales.csv              # Source data
├── sales.db               # Generated SQLite database
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusions
└── README.md             # Project documentation
```

---

## 8. Technology Decisions & Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Agent Framework** | Strands Agents | Lightweight, MCP-native integration |
| **Database** | SQLite | Portable, no external dependencies |
| **ORM** | SQLAlchemy | Flexible, type-safe queries |
| **UI Framework** | Streamlit | Rapid prototyping, Python-native |
| **Charts** | Matplotlib | Lightweight, file-based output |
| **Data Processing** | Pandas | Industry standard for tabular data |
| **IPC Protocol** | MCP (Model Context Protocol) | Standardized, secure tool integration |
| **Database Access** | MCP SQLite Server | Decoupled, controlled access |
| **File Operations** | MCP Filesystem Server | Sandboxed, secure file access |

---

## 9. Agent Capabilities & Limitations

### Capabilities ✓

1. **Query Understanding**
   - Parse natural language sales queries
   - Extract filters, aggregations, and limits
   - Generate equivalent SQL

2. **Data Retrieval**
   - Execute parameterized SQL queries
   - Handle multiple data types
   - Return structured results

3. **Visualization**
   - Generate bar charts
   - Generate line charts
   - Generate pie charts
   - Save to disk for persistent access

4. **Data Export**
   - Export query results to CSV
   - Support batch operations
   - Create persistent reports

### Limitations ⚠️

   - Supports basic SQL (SELECT, GROUP BY, ORDER BY, LIMIT)
   - Fixed chart types (bar, line, pie)


---

## 10. Development Workflow

### Phase 1: Foundation (Complete)
- ✅ Database schema design
- ✅ CSV data loading
- ✅ SQLAlchemy setup

### Phase 2: Agent Core (In Progress)
- 🔄 Strands agent configuration (agent scaffold implemented in `src/agent/sqlite_agent.py`)
- ⚠️ MCP client integration: MCP clients are configured but currently start at module import which can cause startup failures if external executables (e.g., `uvx`) are missing.
- 🔄 Tool definitions (chart tools implemented)

### Phase 3: Visualization (Complete)
- ✅ Chart generation tools (`create_bar_chart`, `create_line_chart`, `create_pie_chart`) implemented
- ✅ Output directory layout created (`src/output/graphs`, `src/output/csv_files`)
- ⏳ Result aggregation (fine-tuning UX and formats)

### Phase 4: UI (Complete)
- ✅ Streamlit interface implemented at `src/main.py` with tabs for Analysis, Data Explorer, Visualizations and Help
- ✅ Query input form, result display, and CSV download functionality present
- ✅ `run.sh` helper and `.env` support added for easier local runs


## 11. API & Tool Contracts

### Tool: `create_bar_chart`
```python
Input:
  - data: str (JSON string of list[dict])
  - x_column: str (column name for x-axis)
  - y_column: str (column name for y-axis)
  - title: str (chart title)
  - filename: str (output filename)

Output:
  - str (confirmation message)

Side Effect:
  - Saves PNG file to src/output/graphs/{filename}
```

---

## 11.1 Operational Notes & Runbook

This section captures actionable operational steps, recent runtime observations, and quick remediation steps to get the app running locally.

- Problem observed: starting Streamlit (`src/main.py`) caused an exception during import because `src/agent/sqlite_agent.py` attempts to start MCP clients using the `uvx` executable which was not found on the system.

- Quick checklist to get a local dev environment running:
  1. Ensure Python virtualenv is activated or use the project's `run.sh` which auto-detects the venv.
  2. Install Node.js/npm if not present (Ubuntu/Debian example):
     ```bash
     sudo apt-get update
     curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
     sudo apt-get install -y nodejs build-essential
     ```
  3. Install `uvx` globally (optional) or use `npx` on-the-fly:
     ```bash
     sudo npm install -g @modelcontextprotocol/uvx || sudo npm install -g uvx
     # Or prefer no-global install and rely on npx when configuring MCP clients
     ```
  4. If you cannot install Node globally, modify the MCP server command to use `npx` or run the server separately and point the client to it.
  5. Recommended code changes for robustness:
     - Add `from dotenv import load_dotenv; load_dotenv()` at the top of `src/main.py` before importing the agent to ensure environment variables are loaded early.
     - Change `sqlite_agent.py` to read `AGENT_MODEL` from `os.getenv('AGENT_MODEL', ...)` instead of hardcoding.
     - Refactor agent initialization into a `get_agent()` function that starts MCP clients on-demand.

- Run the app:
  ```bash
  ./run.sh
  # or
  python -m streamlit run src/main.py
  ```

These steps and code adjustments reduce the chance of startup failures and make the application easier to run in diverse environments.

---
```

### MCP SQLite Client
```python
Input:
  - SQL query (string)

Output:
  - Query result (rows × columns)

Constraints:
  - Read-only operations
  - Database: sales.db
  - Executed via stdio protocol
```

---

## 12. Error Handling Strategy

### Current Design:
- Try-except blocks around chart generation
- JSON parsing validation
- DataFrame type coercion with error handling


## 13. Performance Considerations

### Current Optimizations:
- SQLite for fast local queries
- Pandas for efficient data manipulation
- Matplotlib caching (Agg backend)

### Scalability Concerns:
- CSV data size (manageable up to ~100K rows)
- Chart generation time (O(n) where n = data points)
- MCP server startup overhead

## 14. Testing Strategy


### Manual Testing (Current):
- Test agent with predefined queries
- Verify chart generation
- Validate file exports

---

## 15. Deployment Architecture

### Development Environment:
```
Local Machine
  ├─ Streamlit Server (main.py)
  ├─ Strands Agent (sqlite_agent.py)
  ├─ SQLite (sales.db)
  ├─ MCP Servers (stdio)
  │   ├─ mcp-server-sqlite
  │   └─ server-filesystem
  └─ Output Directory (graphs/, csv_files/)
```


---

## 16. Design Principles

1. **Modularity:** Each component has a single responsibility
2. **Tool-Oriented:** Agent uses composable tools via MCP
3. **Data-Driven:** All decisions based on SQL queries
4. **User-Centric:** Natural language interface
5. **Secure:** Restricted file access, sandboxed operations
6. **Extensible:** Easy to add new tools and chart types

---

## 17. Key Design Files

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `database/DB.py` | DB initialization | `pd.read_csv()`, `df.to_sql()` |
| `src/agent/sqlite_agent.py` | Agent & tools | `@tool`, `MCPClient`, chart functions |
| `src/main.py` | Streamlit UI | Streamlit components |
| `database/callingDB.py` | DB examples | Reference CRUD operations |

---

## 18. Configuration & Environment

### Environment Variables (.env):
```
# Model selection (name or local server identifier)
AGENT_MODEL=qwen.qwen3-next-80b-a3b

# MCP configuration
MCP_SQLITE_DB=./sales.db
MCP_FILESYSTEM_PATH=./src/output/csv_files
MCP_TIMEOUT=120

# Optional external API credentials (only required if using hosted models)
# OPENAI_API_KEY=sk-...
# HUGGINGFACE_HUB_TOKEN=hf_...
# ANTHROPIC_API_KEY=claude-...

# Output paths
OUTPUT_GRAPHS_PATH=./src/output/graphs
OUTPUT_CSV_PATH=./src/output/csv_files

# Local dev flags
ENVIRONMENT=development
DEBUG=true

# Security note: Do NOT commit your real API keys. Add .env to .gitignore.
```

### Dependencies (requirements.txt):
```
sqlalchemy          # ORM
pandas              # Data manipulation
streamlit           # UI
strands-agents      # Agent framework
strands-agents-tools # Pre-built tools
mcp                 # Model Context Protocol
matplotlib          # Charting
python-dotenv       # Load .env into environment
```

### Loading environment variables in code

Add `python-dotenv` and load variables before importing components that rely on environment variables (for example, at the top of `src/main.py`):

```python
from dotenv import load_dotenv
load_dotenv()
# then import modules that read os.environ
from agent.sqlite_agent import ...
```

---

## 29. Summary

This Agentic-AI solution implements a **multi-tool agent architecture** that:

1. **Accepts** natural language queries
2. **Interprets** user intent using an intelligent agent
3. **Executes** database queries via MCP-enabled SQLite
4. **Generates** visualizations through specialized tools
5. **Exports** results to files for persistence
6. **Presents** results through a web UI

The design emphasizes **modularity, extensibility, and security** through the use of the MCP protocol, enabling future integrations with additional data sources, services, and capabilities without modifying core agent logic.
