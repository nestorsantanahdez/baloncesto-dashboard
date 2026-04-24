import pandas as pd
import numpy as np

class StatsCalculator:
    """Calculadora de estadísticas avanzadas de baloncesto"""
    
    @staticmethod
    def calculate_per(df):
        """Player Efficiency Rating (PER)"""
        if df.empty:
            return 0
        
        # Fórmula simplificada de PER
        df['per'] = (df['puntos'] + df['rebotes_tot'] + df['asistencias'] + 
                    df['robos'] + df['tapones_favor'] - 
                    df['perdidas'] - df['faltas_com']) / df['minutos'] * 40 if df['minutos'].mean() > 0 else 0
        return df['per'].mean()
    
    @staticmethod
    def calculate_ts_percentage(df):
        """True Shooting Percentage"""
        if df.empty:
            return 0
        
        puntos = df['puntos'].sum()
        t2_intentados = df['t2_intentados'].sum()
        t3_intentados = df['t3_intentados'].sum()
        tl_intentados = df['tl_intentados'].sum()
        
        total_intentados = t2_intentados + t3_intentados + tl_intentados
        
        if total_intentados == 0:
            return 0
            
        return puntos / (2 * (t2_intentados + t3_intentados) + tl_intentados) * 100
    
    @staticmethod
    def calculate_oreb_percentage(df):
        """Offensive Rebound Percentage"""
        if df.empty:
            return 0
            
        oreb = df['rebotes_of'].sum()
        dreb = df['rebotes_def'].sum()
        total_reb = oreb + dreb
        
        if total_reb == 0:
            return 0
            
        return oreb / total_reb * 100
    
    @staticmethod
    def calculate_ast_to_tov_ratio(df):
        """Assist to Turnover Ratio"""
        if df.empty:
            return 0
            
        ast = df['asistencias'].sum()
        tov = df['perdidas'].sum()
        
        if tov == 0:
            return ast
            
        return ast / tov
    
    @staticmethod
    def calculate_pace(df):
        """Pace (posesiones por partido)"""
        if df.empty:
            return 0
            
        # Fórmula simplificada
        fga = (df['t2_intentados'] + df['t3_intentados']).sum()
        fta = df['tl_intentados'].sum()
        oreb = df['rebotes_of'].sum()
        tov = df['perdidas'].sum()
        
        possessions = fga + 0.44 * fta - oreb + tov
        
        partidos = len(df['partido_id'].unique())
        
        if partidos == 0:
            return 0
            
        return possessions / partidos
    
    @staticmethod
    def calculate_offensive_rating(df):
        """Offensive Rating (puntos por 100 posesiones)"""
        if df.empty:
            return 0
            
        puntos = df['puntos'].sum()
        pace = StatsCalculator.calculate_pace(df)
        
        if pace == 0:
            return 0
            
        return (puntos / pace) * 100
    
    @staticmethod
    def calculate_defensive_rating(df):
        """Defensive Rating (puntos permitidos por 100 posesiones)"""
        # Necesitaríamos datos de puntos permitidos
        # Por ahora devolvemos 0 como placeholder
        return 0
    
    @staticmethod
    def calculate_usage_rate(df):
        """Usage Rate (porcentaje de posesiones usadas)"""
        if df.empty:
            return 0
            
        # Fórmula simplificada
        fga = (df['t2_intentados'] + df['t3_intentados']).sum()
        fta = df['tl_intentados'].sum()
        tov = df['perdidas'].sum()
        ast = df['asistencias'].sum()
        
        possessions = fga + 0.44 * fta - ast + tov
        
        minutos = df['minutos'].sum()
        equipo_minutos = minutos * 5  # Asumiendo 5 jugadores
        
        if equipo_minutos == 0:
            return 0
            
        return (possessions / equipo_minutos) * 100
    
    @staticmethod
    def calculate_advanced_stats(df):
        """Calcula todas las estadísticas avanzadas"""
        if df.empty:
            return {}
            
        return {
            'PER': round(StatsCalculator.calculate_per(df), 2),
            'TS%': round(StatsCalculator.calculate_ts_percentage(df), 2),
            'OREB%': round(StatsCalculator.calculate_oreb_percentage(df), 2),
            'AST/TOV': round(StatsCalculator.calculate_ast_to_tov_ratio(df), 2),
            'PACE': round(StatsCalculator.calculate_pace(df), 2),
            'ORtg': round(StatsCalculator.calculate_offensive_rating(df), 2),
            'USG%': round(StatsCalculator.calculate_usage_rate(df), 2)
        }
    
    @staticmethod
    def calculate_player_impact(df):
        """Calcula el impacto de un jugador en el equipo"""
        if df.empty:
            return 0
            
        # Impacto basado en plus/minus y valoración
        plus_minus = df['plus_minus'].mean() if 'plus_minus' in df.columns else 0
        valoracion = df['valoracion'].mean()
        
        # Normalizar y combinar
        impacto = (plus_minus * 0.6 + valoracion * 0.4)
        
        return round(impacto, 2)
    
    @staticmethod
    def calculate_team_synergy(df):
        """Calcula la sinergia del equipo basada en asistencias"""
        if df.empty:
            return 0
            
        total_puntos = df['puntos'].sum()
        puntos_asistidos = df['asistencias'].sum() * 2  # Asumiendo 2 puntos por asistencia promedio
        
        if total_puntos == 0:
            return 0
            
        return round((puntos_asistidos / total_puntos) * 100, 2)
