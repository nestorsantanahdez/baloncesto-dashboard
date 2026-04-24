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
        "� Depuración de Base de Datos",
        "� Estadísticas por Equipo",
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
        if modulo_seleccionado == "🔍 Depuración de Base de Datos":
            st.header("🔍 Depuración de Base de Datos")
            st.subheader("🔧 Variables de Entorno")
            st.write(f"**SUPABASE_URL:** {'✅ Configurada' if os.getenv('SUPABASE_URL') else '❌ No configurada'}")
            st.write(f"**SUPABASE_KEY:** {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ No configurada'}")
            st.write(f"**DASHBOARD_USER:** {'✅ Configurada' if os.getenv('DASHBOARD_USER') else '❌ No configurada'}")
            st.write(f"**DASHBOARD_PASSWORD:** {'✅ Configurada' if os.getenv('DASHBOARD_PASSWORD') else '❌ No configurada'}")
            
            st.subheader("📊 Datos de Ejemplo")
            import pandas as pd
            data = {
                'Jugador': ['Juan Pérez', 'María García', 'Luis Rodríguez', 'Ana Martínez'],
                'Puntos': [22, 18, 25, 15],
                'Rebotes': [8, 10, 6, 12],
                'Asistencias': [5, 7, 3, 8]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Jugador')['Puntos'])
            
        elif modulo_seleccionado == "📊 Estadísticas por Equipo":
            st.header("📊 Estadísticas por Equipo")
            st.subheader("📈 Estadísticas del Partido")
            import pandas as pd
            data = {
                'Equipo': ['Lakers', 'Warriors', 'Celtics', 'Heat'],
                'Puntos': [110, 105, 98, 102],
                'Rebotes': [45, 42, 38, 40],
                'Asistencias': [25, 28, 22, 24]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Equipo')['Puntos'])
            
        elif modulo_seleccionado == "👥 Análisis de Parejas":
            st.header("👥 Análisis de Parejas")
            st.subheader("🎯 Sinergia Entre Jugadores")
            import pandas as pd
            data = {
                'Pareja': ['Juan-María', 'Luis-Ana', 'Pedro-Sofía'],
                'Asistencias Cruzadas': [12, 8, 15],
                'Eficiencia': [85, 78, 92]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
        elif modulo_seleccionado == "👤 Análisis Individual de Jugadores":
            st.header("👤 Análisis Individual de Jugadores")
            st.subheader("📈 Estadísticas Personales")
            import pandas as pd
            data = {
                'Jugador': ['Juan Pérez', 'María García', 'Luis Rodríguez'],
                'Puntos': [22, 18, 25],
                'Rebotes': [8, 10, 6],
                'Asistencias': [5, 7, 3],
                'Minutos': [32, 28, 35]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Jugador')['Puntos'])
            
        elif modulo_seleccionado == "📊 Comparativas":
            st.header("📊 Comparativas")
            st.subheader("⚔️ Head to Head")
            import pandas as pd
            data = {
                'Métrica': ['Puntos', 'Rebotes', 'Asistencias', 'Eficiencia'],
                'Jugador 1': [22, 8, 5, 85],
                'Jugador 2': [18, 10, 7, 78]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
        elif modulo_seleccionado == "🎯 Análisis de Tiros":
            st.header("🎯 Análisis de Tiros")
            st.subheader("🏀 Estadísticas de Tiro")
            import pandas as pd
            data = {
                'Zona': ['Línea de 3', 'Pintura', 'Media Distancia', 'Banda'],
                'Intentos': [15, 20, 8, 12],
                'Aciertos': [6, 14, 3, 8],
                '% Acierto': [40, 70, 37.5, 66.7]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Zona')['% Acierto'])
            
        elif modulo_seleccionado == "⚔️ Dinámica de Equipo":
            st.header("⚔️ Dinámica de Equipo")
            st.subheader("📊 Distribución de Minutos")
            import pandas as pd
            data = {
                'Jugador': ['Juan Pérez', 'María García', 'Luis Rodríguez', 'Ana Martínez'],
                'Minutos': [32, 28, 35, 25],
                '% Tiempo Juego': [26.7, 23.3, 29.2, 20.8]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Jugador')['Minutos'])
            
        elif modulo_seleccionado == "🏆 Análisis de Rivales":
            st.header("🏆 Análisis de Rivales")
            st.subheader("📈 Estadísticas Contra Oponentes")
            import pandas as pd
            data = {
                'Rival': ['Lakers', 'Warriors', 'Celtics'],
                'Puntos a Favor': [105, 98, 110],
                'Puntos en Contra': [102, 105, 95],
                'Diferencia': [+3, -7, +15]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index('Rival')['Diferencia'])
            
    except Exception as e:
        st.error(f"Error cargando el módulo {modulo_seleccionado}: {e}")
        st.error("Por favor, intenta recargar la página")

if __name__ == "__main__":
    main()
