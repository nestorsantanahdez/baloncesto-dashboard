import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='.env')

# Configuración básica
st.set_page_config(page_title="Dashboard Baloncesto", page_icon="🏀", layout="wide")

# Login con credenciales del .env
def login_form():
    with st.form("login"):
        st.subheader("🔐 Acceso al Dashboard")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Iniciar Sesión")

        if submit_button:
            # Usar credenciales del .env
            correct_user = os.getenv("DASHBOARD_USER")
            correct_pass = os.getenv("DASHBOARD_PASSWORD")
            
            if username == correct_user and password == correct_pass:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# Main
def main():
    # Verificar autenticación
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login_form()
        return

    # Dashboard principal
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
    st.sidebar.write(f"**Base de Datos:** Conectada")
    
    # Botón de logout
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Renderizar módulo seleccionado
    try:
        if modulo_seleccionado == "📊 Estadísticas por Equipo":
            st.header("📊 Estadísticas por Equipo")
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
            data = {
                'Pareja': ['Juan-María', 'Luis-Ana', 'Pedro-Sofía'],
                'Asistencias Cruzadas': [12, 8, 15],
                'Eficiencia': [85, 78, 92]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
        elif modulo_seleccionado == "👤 Análisis Individual de Jugadores":
            st.header("👤 Análisis Individual de Jugadores")
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
            data = {
                'Métrica': ['Puntos', 'Rebotes', 'Asistencias', 'Eficiencia'],
                'Jugador 1': [22, 8, 5, 85],
                'Jugador 2': [18, 10, 7, 78]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
        elif modulo_seleccionado == "🎯 Análisis de Tiros":
            st.header("🎯 Análisis de Tiros")
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
        st.error(f"Error: {e}")
        st.write("Por favor, intenta recargar la página")

if __name__ == "__main__":
    main()
