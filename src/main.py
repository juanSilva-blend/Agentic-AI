import streamlit as st
import os
import time
import glob
from dotenv import load_dotenv
from agent.sqlite_agent import query_sales_agent

st.set_page_config(
    page_title="Sales Intelligence Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Headers - Forzamos color oscuro */
    .main-header {
        font-size: 2.5rem;
        color: #1f2937 !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280 !important;
        margin-bottom: 2rem;
    }
    
    .stChatMessage {
        background-color: white !important;
        border-radius: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Forzar que CUALQUIER texto dentro del chat sea gris oscuro/negro */
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #1f2937 !important; 
    }
    
    /* Botones de descarga */
    .stDownloadButton button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stDownloadButton button:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)
# --- Configuración de Rutas ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHS_DIR = os.path.join(BASE_DIR, "src", "output", "graphs")
CSV_DIR = os.path.join(BASE_DIR, "src", "output", "csv_files")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3094/3094851.png", width=80)
    st.title("Panel de Control")
    st.markdown("---")
    
    st.subheader("🛠️ Acciones")
    if st.button("🗑️ Limpiar Historial", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.subheader("💡 Sugerencias")
    st.info(
        "Prueba preguntando:\n"
        "- *¿Top 5 productos más vendidos?*\n"
        "- *Ventas totales por sede en gráfico de barras*\n"
        "- *Genera un CSV con las ventas de Ana*"
    )
    
    st.markdown("---")
    st.caption("Agentic AI v1.0 • Powered by Strands & MCP")

# --- Área Principal ---

# Cabecera
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-header">🤖 Sales Intelligence Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tu analista de datos personal impulsado por IA. Pregunta, visualiza y exporta.</div>', unsafe_allow_html=True)

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Renderizado del Chat ---
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        # Mensaje de bienvenida si está vacío
        st.markdown(
            """
            <div style="text-align: center; padding: 50px; color: #6b7280;">
                <h3>👋 ¡Hola! Soy tu asistente de ventas.</h3>
                <p>Estoy conectado a tu base de datos SQLite. ¿Qué quieres saber hoy?</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    for message in st.session_state.messages:
        # Elegir avatar según el rol
        avatar = "👤" if message["role"] == "user" else "🤖"
        
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            
            # Mostrar imágenes si existen en el mensaje
            if "image_path" in message:
                try:
                    st.image(message["image_path"], caption="📊 Visualización Generada", use_column_width=True)
                except:
                    st.error("No se pudo cargar la imagen.")
            
            # Mostrar botón de descarga si existe archivo
            if "file_path" in message:
                try:
                    with open(message["file_path"], "rb") as f:
                        st.download_button(
                            label="📥 Descargar Reporte CSV",
                            data=f,
                            file_name=os.path.basename(message["file_path"]),
                            mime="text/csv",
                            key=f"dl_{message['file_path']}" 
                        )
                except:
                    st.error("El archivo ya no está disponible.")

# --- Input del Usuario ---
if prompt := st.chat_input("Escribe tu consulta sobre los datos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        # Contenedor vacío para ir actualizando el estado
        response_container = st.empty()
        
        # Barra de progreso simulada para dar feedback de "pensando"
        progress_text = "Analizando esquema de base de datos..."
        my_bar = st.progress(0, text=progress_text)
        
        timestamp_start = time.time()
        
        try:
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text="Generando consulta SQL y visualizaciones...")
            
            # Ejecutar Agente
            response_text = query_sales_agent(prompt)
            my_bar.empty() # Quitar barra de carga
            
            # Mostrar respuesta
            response_container.markdown(response_text)
            
            generated_img = None
            generated_file = None
            
            # Buscar gráfico
            list_of_files = glob.glob(os.path.join(GRAPHS_DIR, '*'))
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getmtime)
                if os.path.getmtime(latest_file) > timestamp_start:
                    st.image(latest_file, caption="Nueva visualización", use_column_width=True)
                    generated_img = latest_file

            # Buscar CSV
            list_of_csvs = glob.glob(os.path.join(CSV_DIR, '*'))
            if list_of_csvs:
                latest_csv = max(list_of_csvs, key=os.path.getmtime)
                if os.path.getmtime(latest_csv) > timestamp_start:
                    with open(latest_csv, "rb") as f:
                        st.download_button(
                            label="📥 Descargar CSV Generado",
                            data=f,
                            file_name=os.path.basename(latest_csv),
                            mime="text/csv"
                        )
                    generated_file = latest_csv
                    st.success(f"Archivo exportado: {os.path.basename(latest_csv)}")

            # Guardar en historial con metadatos
            msg_data = {"role": "assistant", "content": response_text}
            if generated_img: msg_data["image_path"] = generated_img
            if generated_file: msg_data["file_path"] = generated_file
            
            st.session_state.messages.append(msg_data)

        except Exception as e:
            my_bar.empty()
            st.error(f"❌ Ocurrió un error: {str(e)}")