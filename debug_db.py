import streamlit as st
import pandas as pd
import os
import sys

def debug_database():
    """Módulo de depuración simple"""
    st.header("🔍 Depuración de Base de Datos")
    
    # Variables de entorno
    st.subheader("🔧 Variables de Entorno")
    st.write(f"**SUPABASE_URL:** {'✅ Configurada' if os.getenv('SUPABASE_URL') else '❌ No configurada'}")
    st.write(f"**SUPABASE_KEY:** {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ No configurada'}")
    st.write(f"**DASHBOARD_USER:** {'✅ Configurada' if os.getenv('DASHBOARD_USER') else '❌ No configurada'}")
    st.write(f"**DASHBOARD_PASSWORD:** {'✅ Configurada' if os.getenv('DASHBOARD_PASSWORD') else '❌ No configurada'}")
    
    # Información del sistema
    st.subheader("💻 Información del Sistema")
    st.write(f"**Python versión:** {sys.version}")
    st.write(f"**Pandas versión:** {pd.__version__}")
    st.write(f"**Streamlit versión:** {st.__version__}")
    
    # Intentar importar database
    st.subheader("📦 Estado de la Conexión")
    try:
        st.write("Intentando importar DatabaseManager...")
        from database import DatabaseManager
        st.success("✅ DatabaseManager importado correctamente")
        
        st.write("Intentando crear conexión...")
        db_manager = DatabaseManager()
        st.success("✅ Conexión a base de datos establecida")
        
        st.write("Intentando obtener equipos...")
        equipos = db_manager.get_equipos()
        st.write(f"**Equipos encontrados:** {len(equipos)}")
        
        if equipos:
            st.dataframe(pd.DataFrame(equipos[:10], columns=['Equipos']))
        else:
            st.warning("⚠️ No se encontraron equipos")
            
    except ImportError as e:
        st.error(f"❌ Error importando: {e}")
        st.write("El módulo database.py no se puede importar")
    except Exception as e:
        st.error(f"❌ Error general: {e}")
        st.write("La conexión a la base de datos está fallando")
    
    # Datos de ejemplo
    st.subheader("📊 Datos de Ejemplo (Funcionando)")
    data = {
        'Jugador': ['Juan Pérez', 'María García', 'Luis Rodríguez', 'Ana Martínez'],
        'Puntos': [22, 18, 25, 15],
        'Rebotes': [8, 10, 6, 12],
        'Asistencias': [5, 7, 3, 8],
        'Minutos': [32, 28, 35, 25]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📈 Gráfico de Puntos")
    st.bar_chart(df.set_index('Jugador')['Puntos'])
    
    st.success("✅ Streamlit funciona correctamente")
    st.info("ℹ️ El problema está en la conexión a la base de datos")

if __name__ == "__main__":
    debug_database()
