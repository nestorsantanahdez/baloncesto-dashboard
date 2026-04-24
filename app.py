import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='.env')

# Diccionario de usuarios (fácil de modificar)
USUARIOS = {
    "admin": "baloncesto123",
    "juan": "juan123",
    "maria": "maria456",
    "pedro": "pedro789",
    "ana": "ana456"
}

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
            # Verificar contra el diccionario de usuarios
            if username in USUARIOS and password == USUARIOS[username]:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# Función para inicializar DatabaseManager
@st.cache_resource
def init_database():
    try:
        from database import DatabaseManager
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
    
    # Añadir módulo de administración solo para admin
    if st.session_state.username == "admin":
        modulos_disponibles.append("⚙️ Administración de Usuarios")

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
            st.header("📊 Estadísticas por Equipo")
            
            # Filtros
            col1, col2 = st.columns([2, 1])
            
            with col1:
                equipos = db_manager.get_equipos()
                equipos.insert(0, "Todos")
                equipo_seleccionado = st.selectbox("Seleccionar Equipo", equipos)
            
            with col2:
                ordenar_por = st.selectbox(
                    "Ordenar por",
                    ["puntos", "rebotes_tot", "asistencias", "valoracion", "per"]
                )
            
            # Obtener datos
            if equipo_seleccionado == "Todos":
                df_equipo = db_manager.get_estadisticas_equipos()
            else:
                df_equipo = db_manager.get_estadisticas_equipo(equipo_seleccionado)
            
            if not df_equipo.empty:
                st.subheader("📈 Estadísticas del Equipo")
                st.dataframe(df_equipo, use_container_width=True)
                
                # Gráficos
                st.subheader("📊 Gráficos")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(df_equipo.set_index('equipo_nombre')[ordenar_por])
                
                with col2:
                    if 'puntos' in df_equipo.columns:
                        st.bar_chart(df_equipo.set_index('equipo_nombre')['puntos'])
            else:
                st.warning("No hay datos disponibles para el equipo seleccionado")
                
        elif modulo_seleccionado == "👥 Análisis de Parejas":
            st.header("👥 Análisis de Parejas")
            
            # Selección de jugadores
            col1, col2 = st.columns(2)
            
            with col1:
                jugadores = db_manager.get_jugadores()
                jugador1 = st.selectbox("Jugador 1", jugadores)
            
            with col2:
                jugadores2 = [j for j in jugadores if j != jugador1]
                jugador2 = st.selectbox("Jugador 2", jugadores2)
            
            # Análisis de sinergia
            if jugador1 and jugador2:
                st.subheader(f"🎯 Sinergia: {jugador1} - {jugador2}")
                
                # Datos de ejemplo (debería venir de la BD)
                data = {
                    'Métrica': ['Asistencias Cruzadas', 'Puntos Juntos', 'Eficiencia'],
                    'Valor': [12, 45, 85]
                }
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Seleccione dos jugadores para el análisis")
                
        elif modulo_seleccionado == "👤 Análisis Individual de Jugadores":
            st.header("👤 Análisis Individual de Jugadores")
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                jugadores = db_manager.get_jugadores()
                jugador_seleccionado = st.selectbox("Seleccionar Jugador", jugadores)
            
            with col2:
                posiciones = ["Todas", "Base", "Escolta", "Alero", "Ala-Pívot", "Pívot"]
                posicion_filtro = st.selectbox("Posición", posiciones)
            
            with col3:
                edades = ["Todas", "18-25", "26-30", "31-35", "36+"]
                edad_filtro = st.selectbox("Rango de Edad", edades)
            
            # Estadísticas del jugador
            if jugador_seleccionado:
                st.subheader(f"📈 Estadísticas de {jugador_seleccionado}")
                
                stats = db_manager.get_estadisticas_jugadores(jugador_seleccionado)
                if not stats.empty:
                    st.dataframe(stats, use_container_width=True)
                    
                    # Gráficos
                    st.subheader("📊 Análisis de Rendimiento")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'puntos' in stats.columns:
                            st.bar_chart(stats.set_index('nombre_jugador')['puntos'])
                    
                    with col2:
                        if 'valoracion' in stats.columns:
                            st.bar_chart(stats.set_index('nombre_jugador')['valoracion'])
                else:
                    st.warning("No hay estadísticas disponibles para este jugador")
            else:
                st.warning("Seleccione un jugador para ver sus estadísticas")
                
        elif modulo_seleccionado == "📊 Comparativas":
            st.header("📊 Comparativas")
            
            # Comparación de equipos
            col1, col2 = st.columns(2)
            
            with col1:
                equipos = db_manager.get_equipos()
                equipo1 = st.selectbox("Equipo 1", equipos)
            
            with col2:
                equipos2 = [e for e in equipos if e != equipo1]
                equipo2 = st.selectbox("Equipo 2", equipos2)
            
            if equipo1 and equipo2:
                st.subheader(f"⚔️ {equipo1} vs {equipo2}")
                
                # Estadísticas comparativas
                stats1 = db_manager.get_estadisticas_equipo(equipo1)
                stats2 = db_manager.get_estadisticas_equipo(equipo2)
                
                if not stats1.empty and not stats2.empty:
                    # Tabla comparativa
                    comparison_data = {
                        'Métrica': ['Puntos', 'Rebotes', 'Asistencias', 'Valoración'],
                        equipo1: [stats1['puntos'].iloc[0], stats1['rebotes_tot'].iloc[0], 
                               stats1['asistencias'].iloc[0], stats1['valoracion'].iloc[0]],
                        equipo2: [stats2['puntos'].iloc[0], stats2['rebotes_tot'].iloc[0], 
                               stats2['asistencias'].iloc[0], stats2['valoracion'].iloc[0]]
                    }
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True)
                    
                    # Gráfico comparativo
                    st.subheader("📊 Gráfico Comparativo")
                    comparison_df = df_comparison.set_index('Métrica')
                    st.bar_chart(comparison_df)
                else:
                    st.warning("No hay estadísticas disponibles para la comparación")
            else:
                st.warning("Seleccione dos equipos para comparar")
                
        elif modulo_seleccionado == "🎯 Análisis de Tiros":
            st.header("🎯 Análisis de Tiros")
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                jugadores = db_manager.get_jugadores()
                jugador_seleccionado = st.selectbox("Seleccionar Jugador", jugadores)
            
            with col2:
                zonas = ["Todas", "Línea de 3", "Pintura", "Media Distancia", "Banda"]
                zona_filtro = st.selectbox("Zona de Tiro", zonas)
            
            if jugador_seleccionado:
                st.subheader(f"🏀 Estadísticas de Tiro - {jugador_seleccionado}")
                
                # Datos de ejemplo (deberían venir de la BD)
                shooting_data = {
                    'Zona': ['Línea de 3', 'Pintura', 'Media Distancia', 'Banda'],
                    'Intentos': [15, 20, 8, 12],
                    'Aciertos': [6, 14, 3, 8],
                    '% Acierto': [40.0, 70.0, 37.5, 66.7]
                }
                df_shooting = pd.DataFrame(shooting_data)
                st.dataframe(df_shooting, use_container_width=True)
                
                # Gráfico de efectividad
                st.subheader("📈 Efectividad por Zona")
                st.bar_chart(df_shooting.set_index('Zona')['% Acierto'])
            else:
                st.warning("Seleccione un jugador para ver sus estadísticas de tiro")
                
        elif modulo_seleccionado == "⚔️ Dinámica de Equipo":
            st.header("⚔️ Dinámica de Equipo")
            
            # Selección de equipo
            equipos = db_manager.get_equipos()
            equipo_seleccionado = st.selectbox("Seleccionar Equipo", equipos)
            
            if equipo_seleccionado:
                st.subheader(f"👥 Dinámica - {equipo_seleccionado}")
                
                # Distribución de minutos
                jugadores_equipo = db_manager.get_estadisticas_jugadores(equipo_seleccionado)
                if not jugadores_equipo.empty:
                    st.subheader("📊 Distribución de Minutos")
                    st.dataframe(jugadores_equipo[['nombre_jugador', 'minutos']], use_container_width=True)
                    st.bar_chart(jugadores_equipo.set_index('nombre_jugador')['minutos'])
                    
                    # Estadísticas del quinteto
                    st.subheader("🏀 Estadísticas del Quinteto")
                    quinteto_stats = jugadores_equipo.nlargest(5, 'minutos')
                    st.dataframe(quinteto_stats, use_container_width=True)
                else:
                    st.warning("No hay datos de jugadores disponibles para este equipo")
            else:
                st.warning("Seleccione un equipo para ver su dinámica")
                
        elif modulo_seleccionado == "🏆 Análisis de Rivales":
            st.header("🏆 Análisis de Rivales")
            
            # Selección de equipo y rival
            col1, col2 = st.columns(2)
            
            with col1:
                equipos = db_manager.get_equipos()
                equipo_principal = st.selectbox("Tu Equipo", equipos)
            
            with col2:
                rivales = [e for e in equipos if e != equipo_principal]
                equipo_rival = st.selectbox("Equipo Rival", rivales)
            
            if equipo_principal and equipo_rival:
                st.subheader(f"⚔️ {equipo_principal} vs {equipo_rival}")
                
                # Estadísticas head-to-head
                stats_principal = db_manager.get_estadisticas_equipo(equipo_principal)
                stats_rival = db_manager.get_estadisticas_equipo(equipo_rival)
                
                if not stats_principal.empty and not stats_rival.empty:
                    # Análisis de matchups
                    st.subheader("📊 Análisis de Matchups")
                    
                    matchup_data = {
                        'Métrica': ['Puntos', 'Rebotes', 'Asistencias', 'Eficiencia Defensiva'],
                        equipo_principal: [stats_principal['puntos'].iloc[0], stats_principal['rebotes_tot'].iloc[0],
                                       stats_principal['asistencias'].iloc[0], 85],
                        equipo_rival: [stats_rival['puntos'].iloc[0], stats_rival['rebotes_tot'].iloc[0],
                                     stats_rival['asistencias'].iloc[0], 78]
                    }
                    df_matchup = pd.DataFrame(matchup_data)
                    st.dataframe(df_matchup, use_container_width=True)
                    
                    # Predicción basada en estadísticas
                    st.subheader("🔮 Predicción")
                    puntos_principal = stats_principal['puntos'].iloc[0]
                    puntos_rival = stats_rival['puntos'].iloc[0]
                    
                    if puntos_principal > puntos_rival:
                        st.success(f"🏀 {equipo_principal} tiene ventaja basada en estadísticas")
                    elif puntos_rival > puntos_principal:
                        st.warning(f"⚠️ {equipo_rival} tiene ventaja basada en estadísticas")
                    else:
                        st.info("⚖️ Equipos muy parecidos estadísticamente")
                else:
                    st.warning("No hay estadísticas disponibles para el análisis")
            else:
                st.warning("Seleccione dos equipos para el análisis de rivales")
                
        elif modulo_seleccionado == "⚙️ Administración de Usuarios":
            st.header("⚙️ Administración de Usuarios")
            st.warning("⚠️ Solo el administrador puede ver esta sección")
            
            # Mostrar usuarios actuales
            st.subheader("📋 Usuarios Actuales")
            usuarios_df = pd.DataFrame(list(USUARIOS.items()), columns=['Usuario', 'Contraseña'])
            usuarios_df['Contraseña'] = '********'  # Ocultar contraseñas
            st.dataframe(usuarios_df, use_container_width=True)
            
            # Formulario para añadir usuario
            st.subheader("➕ Añadir Nuevo Usuario")
            
            with st.form("add_user"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nuevo_usuario = st.text_input("Nuevo Usuario", key="nuevo_usuario")
                
                with col2:
                    nueva_password = st.text_input("Contraseña", type="password", key="nueva_password")
                
                submit_add = st.form_submit_button("Añadir Usuario")
                
                if submit_add:
                    if nuevo_usuario and nueva_password:
                        if nuevo_usuario in USUARIOS:
                            st.error("❌ Este usuario ya existe")
                        else:
                            # Añadir usuario al diccionario
                            USUARIOS[nuevo_usuario] = nueva_password
                            st.success(f"✅ Usuario '{nuevo_usuario}' añadido correctamente")
                            st.rerun()
                    else:
                        st.error("❌ Por favor, complete todos los campos")
            
            # Formulario para eliminar usuario
            st.subheader("🗑️ Eliminar Usuario")
            
            with st.form("delete_user"):
                usuarios_para_eliminar = [u for u in USUARIOS.keys() if u != "admin"]  # No eliminar admin
                if usuarios_para_eliminar:
                    usuario_a_eliminar = st.selectbox("Seleccionar Usuario a Eliminar", usuarios_para_eliminar)
                    submit_delete = st.form_submit_button("Eliminar Usuario")
                    
                    if submit_delete:
                        del USUARIOS[usuario_a_eliminar]
                        st.success(f"✅ Usuario '{usuario_a_eliminar}' eliminado correctamente")
                        st.rerun()
                else:
                    st.info("No hay usuarios adicionales para eliminar")
            
            # Información importante
            st.markdown("---")
            st.info("ℹ️ **Nota:** Los cambios se perderán si reinicias la aplicación. Para cambios permanentes, considera usar una base de datos.")

    except Exception as e:
        st.error(f"Error cargando el módulo {modulo_seleccionado}: {e}")
        st.error("Por favor, intenta recargar la página")

if __name__ == "__main__":
    main()
