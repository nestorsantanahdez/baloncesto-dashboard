import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='.env')

class Config:
    """Clase de configuración para el dashboard de baloncesto"""
    
    # Credenciales de Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Credenciales de autenticación del dashboard
    DASHBOARD_USER = os.getenv("DASHBOARD_USER")
    DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")
    
    # Configuración de caché
    CACHE_TTL = 300  # 5 minutos
    
    # Configuración del dashboard
    DASHBOARD_TITLE = "Dashboard Estadísticas Baloncesto"
    DASHBOARD_LAYOUT = "wide"
    
    # Configuración de gráficos
    CHART_THEME = "plotly_white"
    CHART_HEIGHT = 500
    
    @staticmethod
    def validate_required_env_vars():
        """Valida que las variables de entorno requeridas estén configuradas"""
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_KEY", 
            "DASHBOARD_USER",
            "DASHBOARD_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Faltan variables de entorno requeridas: {', '.join(missing_vars)}")
        
        return True
    
    @staticmethod
    def get_database_config():
        """Devuelve la configuración de la base de datos"""
        return {
            "url": Config.SUPABASE_URL,
            "key": Config.SUPABASE_KEY
        }
    
    @staticmethod
    def get_auth_config():
        """Devuelve la configuración de autenticación"""
        return {
            "username": Config.DASHBOARD_USER,
            "password": Config.DASHBOARD_PASSWORD
        }
