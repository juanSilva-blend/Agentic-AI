import streamlit as st
import os
import sys
import asyncio

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.sqlite_agent import get_agent_response_async

# Streamlit UI
st.title("📊 Sales Data Analysis Agent")

st.markdown("""
Welcome! I'm your AI assistant for analyzing sales data and creates graphs or CSVs.

Ask me questions like:
- **"Top 5 productos más vendidos en Medellín"**
- **"Vendedor con más ventas en Bogotá, hazme un gráfico circular"**
- **"Guarda las ventas por vendedor en un archivo CSV"**
""")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📚 Quick Queries")
    query = st.selectbox("Select a query:", [
        "Choose a query...",
        "Top 5 productos más vendidos en Medellín",
        "Quién fue el vendedor con más ventas en Bogotá. Genera un grafico circular para mostrar los datos",
        "Guarda las ventas por vendedor en un archivo CSV",
        "Haz un Resumen general de las ventas de 2025, hazme tambien un gráfico de líneas"
    ])
    
    if query != "Choose a query..." and st.button("Ask this"):
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.pending_response = True
        st.rerun()
    
    st.divider()
    
    st.header("📈 Generated Graphs")
    graphs_dir = "./src/output/graphs"
    if os.path.exists(graphs_dir):
        graphs = [f for f in os.listdir(graphs_dir) if f.endswith('.png')]
        if graphs:
            selected_graph = st.selectbox("View graph:", ["Select..."] + graphs)
            if selected_graph != "Select...":
                st.image(os.path.join(graphs_dir, selected_graph), caption=selected_graph)
        else:
            st.info("No graphs generated yet")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me about sales data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.pending_response = True
    st.rerun()

# Process pending response
if st.session_state.get("pending_response", False):
    last_message = st.session_state.messages[-1]["content"]
    
    with st.spinner("Analyzing data..."):
        try:
            response = asyncio.run(get_agent_response_async(last_message))
        except Exception as e:
            response = f"Error: {str(e)}"
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.pending_response = False
    st.rerun()

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()