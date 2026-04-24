import streamlit as st
import pandas as pd
from database import DatabaseManager

def debug_database():
    """Módulo de depuración para verificar la conexión y datos"""
    st.header("🔍 Depuración de Base de Datos")
    
    try:
        # Inicializar conexión
        db_manager = DatabaseManager()
        st.success("✅ Conexión a base de datos exitosa")
        
        # Verificar tablas
        st.subheader("📋 Verificación de Tablas")
        
        # Obtener equipos
        try:
            equipos = db_manager.get_equipos()
            st.write(f"**Equipos encontrados:** {len(equipos)}")
            if equipos:
                st.write(equipos[:10])  # Mostrar primeros 10
        except Exception as e:
            st.error(f"Error obteniendo equipos: {e}")
        
        # Obtener jugadores
        try:
            jugadores = db_manager.get_jugadores()
            st.write(f"**Jugadores encontrados:** {len(jugadores)}")
            if jugadores:
                st.write(jugadores[:10])  # Mostrar primeros 10
        except Exception as e:
            st.error(f"Error obteniendo jugadores: {e}")
        
        # Obtener estadísticas
        try:
            stats = db_manager.get_estadisticas_jugadores()
            st.write(f"**Estadísticas encontradas:** {len(stats)} filas")
            if not stats.empty:
                st.write("**Columnas disponibles:**")
                st.write(stats.columns.tolist())
                st.write("**Primeras filas:**")
                st.dataframe(stats.head())
        except Exception as e:
            st.error(f"Error obteniendo estadísticas: {e}")
        
        # Verificar partidos
        try:
            partidos = db_manager.get_partidos()
            st.write(f"**Partidos encontrados:** {len(partidos)} filas")
            if not partidos.empty:
                st.dataframe(partidos.head())
        except Exception as e:
            st.error(f"Error obteniendo partidos: {e}")
            
    except Exception as e:
        st.error(f"Error general: {e}")
        st.error("Revisa las variables de entorno en Streamlit Cloud")

if __name__ == "__main__":
    debug_database()
