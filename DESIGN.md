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

1. **Current Scope**
   - Supports basic SQL (SELECT, GROUP BY, ORDER BY, LIMIT)
   - No INSERT/UPDATE/DELETE operations
   - Fixed chart types (bar, line, pie)
   - No real-time data streaming

2. **Security Considerations**
   - File access restricted to `src/output/`
   - SQL injection prevention via MCP
   - No user authentication (future enhancement)

---

## 10. Development Workflow

### Phase 1: Foundation (Complete)
- ✅ Database schema design
- ✅ CSV data loading
- ✅ SQLAlchemy setup

### Phase 2: Agent Core (In Progress)
- 🔄 Strands agent configuration
- 🔄 MCP client integration
- 🔄 Tool definitions

### Phase 3: Visualization (Planned)
- ⏳ Chart generation tools
- ⏳ Output directory management
- ⏳ Result aggregation

### Phase 4: UI (Planned)
- ⏳ Streamlit interface
- ⏳ Query input form
- ⏳ Results display
- ⏳ File download functionality

### Phase 5: Testing & Polish (Planned)
- ⏳ Unit tests
- ⏳ Integration tests
- ⏳ Documentation
- ⏳ Error handling

---

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

### Future Enhancements:
- User-friendly error messages
- Fallback visualizations
- Query validation before execution
- Logging and monitoring

---

## 13. Performance Considerations

### Current Optimizations:
- SQLite for fast local queries
- Pandas for efficient data manipulation
- Matplotlib caching (Agg backend)

### Scalability Concerns:
- CSV data size (manageable up to ~100K rows)
- Chart generation time (O(n) where n = data points)
- MCP server startup overhead

### Future Improvements:
- Query result caching
- Async chart generation
- Batch operations
- Database indexing on common filters

---

## 14. Testing Strategy

### Unit Tests (Planned):
- Chart generation with sample data
- MCP client initialization
- SQL query generation
- File I/O operations

### Integration Tests (Planned):
- End-to-end query → visualization flow
- Agent decision making
- MCP server communication
- CSV export validation

### Manual Testing (Current):
- Test agent with predefined queries
- Verify chart generation
- Validate file exports

---

## 15. Future Enhancements

### Short-term:
- [ ] Add more chart types (scatter, heatmap)
- [ ] Implement query caching
- [ ] Add error recovery mechanisms
- [ ] Create configuration file for customization

### Medium-term:
- [ ] Support for multiple databases
- [ ] User authentication & authorization
- [ ] Query history & favorites
- [ ] Advanced filtering UI

### Long-term:
- [ ] Real-time data streaming
- [ ] Predictive analytics
- [ ] Multi-language support
- [ ] Mobile app integration

---

## 16. Deployment Architecture

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

### Production Deployment (Future):
```
Docker Container
  ├─ Python Runtime
  ├─ Streamlit Server
  ├─ SQLite Database
  ├─ MCP Server Instances
  └─ Volume Mounts
      ├─ Database File
      └─ Output Directory
```

---

## 17. Design Principles

1. **Modularity:** Each component has a single responsibility
2. **Tool-Oriented:** Agent uses composable tools via MCP
3. **Data-Driven:** All decisions based on SQL queries
4. **User-Centric:** Natural language interface
5. **Secure:** Restricted file access, sandboxed operations
6. **Extensible:** Easy to add new tools and chart types

---

## 18. Key Design Files

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `database/DB.py` | DB initialization | `pd.read_csv()`, `df.to_sql()` |
| `src/agent/sqlite_agent.py` | Agent & tools | `@tool`, `MCPClient`, chart functions |
| `src/main.py` | Streamlit UI | Streamlit components |
| `database/callingDB.py` | DB examples | Reference CRUD operations |

---

## 19. Configuration & Environment

### Environment Variables (.env):
```
AGENT_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
MCP_SQLITE_DB=./sales.db
MCP_FILESYSTEM_PATH=./src/output/csv_files
OUTPUT_GRAPHS_PATH=./src/output/graphs
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
```

---

## 20. Summary

This Agentic-AI solution implements a **multi-tool agent architecture** that:

1. **Accepts** natural language queries
2. **Interprets** user intent using an intelligent agent
3. **Executes** database queries via MCP-enabled SQLite
4. **Generates** visualizations through specialized tools
5. **Exports** results to files for persistence
6. **Presents** results through a web UI

The design emphasizes **modularity, extensibility, and security** through the use of the MCP protocol, enabling future integrations with additional data sources, services, and capabilities without modifying core agent logic.
