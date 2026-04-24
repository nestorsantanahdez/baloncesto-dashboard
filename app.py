import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from database import DatabaseManager
from modules.team_stats import TeamStatsModule
from modules.pair_analysis import PairAnalysisModule
from modules.player_analysis import PlayerAnalysisModule
from modules.comparisons import ComparisonsModule
from modules.shooting_analysis import ShootingAnalysisModule
from modules.team_dynamics import TeamDynamicsModule
from modules.rival_analysis import RivalAnalysisModule
from config import Config

# Cargar variables de entorno explícitamente
load_dotenv(dotenv_path='.env')

# Verificar que las variables estén cargadas
if not os.getenv("SUPABASE_URL"):
    st.error("❌ Error: SUPABASE_URL no está configurada en el archivo .env")
    st.stop()

if not os.getenv("SUPABASE_KEY"):
    st.error("❌ Error: SUPABASE_KEY no está configurada en el archivo .env")
    st.stop()

if not os.getenv("DASHBOARD_USER"):
    st.error("❌ Error: DASHBOARD_USER no está configurada en el archivo .env")
    st.stop()

if not os.getenv("DASHBOARD_PASSWORD"):
    st.error("❌ Error: DASHBOARD_PASSWORD no está configurada en el archivo .env")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Estadísticas Baloncesto",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función de autenticación
def login_form():
    with st.form("login"):
        st.subheader("🔐 Acceso al Dashboard")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Iniciar Sesión")
        
        if submit_button:
            if username == os.getenv("DASHBOARD_USER") and password == os.getenv("DASHBOARD_PASSWORD"):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# Función para inicializar DatabaseManager
@st.cache_resource
def init_database():
    try:
        return DatabaseManager()
    except Exception as e:
        st.error(f"Error inicializando DatabaseManager: {e}")
        return None

# Interfaz principal
def main():
    # Verificar autenticación
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_form()
        return
    
    # Inicializar DatabaseManager
    db_manager = init_database()
    
    if db_manager is None:
        st.error("No se pudo conectar a la base de datos")
        return
    
    # Header
    st.title("🏀 Dashboard Profesional de Baloncesto")
    st.markdown(f"Bienvenido, **{st.session_state.username}**")
    
    # Sidebar para navegación
    st.sidebar.header("📊 Navegación")
    
    # Seleccionar módulo
    modulos_disponibles = [
        "📊 Estadísticas por Equipo",
        "👥 Análisis de Parejas", 
        "👤 Análisis Individual de Jugadores",
        "📊 Comparativas",
        "🎯 Análisis de Tiros",
        "⚔️ Dinámica de Equipo",
        "🏆 Análisis de Rivales"
    ]
    
    modulo_seleccionado = st.sidebar.selectbox(
        "Seleccionar Módulo",
        modulos_disponibles,
        index=0
    )
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Información")
    st.sidebar.write(f"**Usuario:** {st.session_state.username}")
    st.sidebar.write(f"**Base de Datos:** Supabase")
    
    # Botón de logout
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Renderizar módulo seleccionado
    try:
        if modulo_seleccionado == "📊 Estadísticas por Equipo":
            TeamStatsModule.render(db_manager)
        elif modulo_seleccionado == "👥 Análisis de Parejas":
            PairAnalysisModule.render(db_manager)
        elif modulo_seleccionado == "👤 Análisis Individual de Jugadores":
            PlayerAnalysisModule.render(db_manager)
        elif modulo_seleccionado == "📊 Comparativas":
            ComparisonsModule.render(db_manager)
        elif modulo_seleccionado == "🎯 Análisis de Tiros":
            ShootingAnalysisModule.render(db_manager)
        elif modulo_seleccionado == "⚔️ Dinámica de Equipo":
            TeamDynamicsModule.render(db_manager)
        elif modulo_seleccionado == "🏆 Análisis de Rivales":
            RivalAnalysisModule.render(db_manager)
            
    except Exception as e:
        st.error(f"Error cargando el módulo {modulo_seleccionado}: {e}")
        st.error("Por favor, intenta recargar la página")

if __name__ == "__main__":
    main()
