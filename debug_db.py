import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

def debug_database():
    """Módulo de depuración ultra-simple"""
    st.header("🔍 Depuración de Base de Datos")
    
    # Mostrar variables de entorno
    st.subheader("🔧 Variables de Entorno")
    st.write(f"**SUPABASE_URL:** {'✅ Configurada' if os.getenv('SUPABASE_URL') else '❌ No configurada'}")
    st.write(f"**SUPABASE_KEY:** {'✅ Configurada' if os.getenv('SUPABASE_KEY') else '❌ No configurada'}")
    st.write(f"**DASHBOARD_USER:** {'✅ Configurada' if os.getenv('DASHBOARD_USER') else '❌ No configurada'}")
    st.write(f"**DASHBOARD_PASSWORD:** {'✅ Configurada' if os.getenv('DASHBOARD_PASSWORD') else '❌ No configurada'}")
    
    # Intentar importar database
    st.subheader("� Importación de Módulos")
    try:
        from database import DatabaseManager
        st.success("✅ DatabaseManager importado correctamente")
        
        # Intentar crear instancia
        try:
            db_manager = DatabaseManager()
            st.success("✅ DatabaseManager creado correctamente")
            
            # Intentar obtener equipos
            try:
                equipos = db_manager.get_equipos()
                st.write(f"**Equipos encontrados:** {len(equipos)}")
                if equipos:
                    st.write(equipos[:5])
                else:
                    st.warning("⚠️ No se encontraron equipos")
            except Exception as e:
                st.error(f"❌ Error obteniendo equipos: {e}")
                st.code(str(e))
                
        except Exception as e:
            st.error(f"❌ Error creando DatabaseManager: {e}")
            st.code(str(e))
            
    except Exception as e:
        st.error(f"❌ Error importando DatabaseManager: {e}")
        st.code(str(e))
    
    # Mostrar información del sistema
    st.subheader("💻 Información del Sistema")
    st.write(f"**Python versión:** {pd.__version__}")
    st.write(f"**Streamlit versión:** {st.__version__}")
    
    # Datos de prueba
    st.subheader("📊 Datos de Prueba")
    data = {
        'Jugador': ['Test 1', 'Test 2', 'Test 3'],
        'Puntos': [10, 15, 20],
        'Rebotes': [5, 8, 6]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
    st.bar_chart(df.set_index('Jugador')['Puntos'])

if __name__ == "__main__":
    debug_database()
