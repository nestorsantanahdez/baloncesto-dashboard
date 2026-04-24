import pandas as pd
import numpy as np
from datetime import datetime

class DataHelpers:
    """Clase de ayuda para procesamiento de datos"""
    
    @staticmethod
    def format_minutes(minutes):
        """Formatea minutos a formato MM:SS"""
        if pd.isna(minutes) or minutes == 0:
            return "00:00"
            
        mins = int(minutes)
        secs = int((minutes - mins) * 60)
        return f"{mins:02d}:{secs:02d}"
    
    @staticmethod
    def get_performance_rating(valoracion):
        """Devuelve rating basado en valoración"""
        if pd.isna(valoracion):
            return "N/A"
            
        if valoracion >= 30:
            return "Excelente"
        elif valoracion >= 20:
            return "Muy Bueno"
        elif valoracion >= 10:
            return "Bueno"
        elif valoracion >= 0:
            return "Regular"
        else:
            return "Pobre"
    
    @staticmethod
    def highlight_best_values(df, columns, ascending=False):
        """Resalta los mejores valores en un DataFrame"""
        if df.empty or len(columns) == 0:
            return df
            
        df_styled = df.copy()
        
        for col in columns:
            if col in df_styled.columns:
                best_value = df_styled[col].max() if not ascending else df_styled[col].min()
                df_styled[col] = df_styled[col].apply(
                    lambda x: f"**{x}**" if x == best_value else x
                )
        
        return df_styled
    
    @staticmethod
    def get_team_color(equipo_nombre):
        """Devuelve color asociado a un equipo (placeholder)"""
        team_colors = {
            "Lakers": "#FDB927",
            "Celtics": "#007A33",
            "Warriors": "#1D428A",
            "Heat": "#98002E",
            "Bulls": "#CE1141",
            "Lakers": "#FDB927",
            "Celtics": "#007A33",
        }
        
        return team_colors.get(equipo_nombre, "#808080")
    
    @staticmethod
    def calculate_win_loss_record(df):
        """Calcula récord de victorias/derrotas"""
        if df.empty:
            return {"victorias": 0, "derrotas": 0, "porcentaje": 0.0}
            
        # Asumiendo que hay una columna 'resultado' o similar
        if 'resultado' in df.columns:
            victorias = len(df[df['resultado'] == 'V'])
            derrotas = len(df[df['resultado'] == 'D'])
        else:
            # Si no hay resultado, usamos plus/minus positivo como victoria
            victorias = len(df[df['plus_minus'] > 0])
            derrotas = len(df[df['plus_minus'] <= 0])
        
        total = victorias + derrotas
        porcentaje = (victorias / total * 100) if total > 0 else 0.0
        
        return {
            "victorias": victorias,
            "derrotas": derrotas,
            "porcentaje": round(porcentaje, 1)
        }
    
    @staticmethod
    def get_streaks(df, player_col='nombre_jugador', result_col='plus_minus'):
        """Calcula rachas de victorias/derrotas"""
        if df.empty:
            return {"current_streak": 0, "best_streak": 0, "worst_streak": 0}
            
        # Ordenar por fecha
        df_sorted = df.sort_values('created_at')
        
        current_streak = 0
        best_streak = 0
        worst_streak = 0
        temp_streak = 0
        
        for _, row in df_sorted.iterrows():
            if row[result_col] > 0:  # Victoria
                if current_streak >= 0:
                    current_streak += 1
                else:
                    current_streak = 1
                temp_streak = current_streak
            else:  # Derrota
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                temp_streak = abs(current_streak)
            
            best_streak = max(best_streak, temp_streak)
            worst_streak = max(worst_streak, current_streak)
        
        return {
            "current_streak": current_streak,
            "best_streak": best_streak,
            "worst_streak": worst_streak
        }
    
    @staticmethod
    def filter_by_performance(df, min_valoracion=10):
        """Filtra jugadores por rendimiento mínimo"""
        if df.empty or 'valoracion' not in df.columns:
            return df
            
        return df[df['valoracion'] >= min_valoracion]
    
    @staticmethod
    def get_top_performers(df, metric_col, n=5):
        """Devuelve los mejores n jugadores en una métrica"""
        if df.empty or metric_col not in df.columns:
            return pd.DataFrame()
            
        return df.nlargest(n, metric_col)
    
    @staticmethod
    def calculate_team_consistency(df):
        """Calcula la consistencia del equipo"""
        if df.empty:
            return 0.0
            
        # Usar desviación estándar de la valoración
        if 'valoracion' in df.columns:
            consistency = 100 - (df['valoracion'].std() / df['valoracion'].mean() * 100)
            return max(0, round(consistency, 1))
        
        return 0.0
    
    @staticmethod
    def get_clutch_stats(df, minutes_threshold=40):
        """Estadísticas en momentos clave (últimos minutos)"""
        if df.empty:
            return pd.DataFrame()
            
        # Filtrar partidos donde el jugador jugó más de X minutos
        clutch_games = df[df['minutos'] >= minutes_threshold]
        
        return clutch_games
    
    @staticmethod
    def create_player_profile(df, player_name):
        """Crea perfil completo de un jugador"""
        if df.empty:
            return {}
            
        player_data = df[df['nombre_jugador'] == player_name]
        
        if player_data.empty:
            return {}
        
        # Estadísticas básicas
        avg_stats = player_data.mean(numeric_only=True)
        
        # Estadísticas totales
        total_stats = player_data.sum(numeric_only=True)
        
        # Partidos jugados
        partidos_jugados = len(player_data)
        
        return {
            'nombre': player_name,
            'partidos_jugados': partidos_jugados,
            'promedios': avg_stats.to_dict(),
            'totales': total_stats.to_dict(),
            'mejor_partido': player_data.loc[player_data['valoracion'].idxmax()].to_dict() if not player_data.empty else {}
        }

class FilterHelpers:
    """Clase de ayuda para filtros complejos"""
    
    @staticmethod
    def filter_by_position(df, position):
        """Filtra jugadores por posición"""
        if df.empty or 'posicion' not in df.columns:
            return df
            
        return df[df['posicion'] == position]
    
    @staticmethod
    def filter_by_age_range(df, min_age, max_age):
        """Filtra jugadores por rango de edad"""
        if df.empty or 'edad' not in df.columns:
            return df
            
        return df[(df['edad'] >= min_age) & (df['edad'] <= max_age)]
    
    @staticmethod
    def filter_by_stat_range(df, stat_col, min_val, max_val):
        """Filtra por rango de estadísticas"""
        if df.empty or stat_col not in df.columns:
            return df
            
        return df[(df[stat_col] >= min_val) & (df[stat_col] <= max_val)]
    
    @staticmethod
    def filter_by_home_away(df, location):
        """Filtra por local/visitante"""
        if df.empty or 'ubicacion' not in df.columns:
            return df
            
        return df[df['ubicacion'] == location]
    
    @staticmethod
    def filter_by_win_loss(df, result):
        """Filtra por victoria/derrota"""
        if df.empty:
            return df
            
        if 'resultado' in df.columns:
            return df[df['resultado'] == result]
        elif 'plus_minus' in df.columns:
            if result == 'V':
                return df[df['plus_minus'] > 0]
            else:
                return df[df['plus_minus'] <= 0]
        
        return df
