import supabase
import pandas as pd
from config import Config
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

class DatabaseManager:
    """Gestor de conexión y consultas a la base de datos de baloncesto"""
    
    def __init__(self):
        try:
            self.client = supabase.create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
        except Exception as e:
            raise Exception(f"Error connecting to Supabase: {e}")
    
    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        try:
            # Intentar obtener datos de una tabla pequeña
            response = self.client.table('equipos').select('count').execute()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_equipos(self):
        """Obtiene todos los equipos"""
        try:
            response = self.client.table('equipos').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                return df['nombre'].tolist() if 'nombre' in df.columns else []
            return []
        except Exception as e:
            print(f"Error getting equipos: {e}")
            return []
    
    def get_jugadores(self):
        """Obtiene todos los jugadores con sus equipos"""
        try:
            # Obtener IDs únicos de jugadores
            response = self.client.table('jugadores_partido').select('jugador_id').execute()
            if not response.data:
                return []
            
            jugador_ids = list(set([item['jugador_id'] for item in response.data]))
            
            # Obtener nombres de jugadores
            jugadores = []
            for jug_id in jugador_ids:
                try:
                    jug_response = self.client.table('jugadores').select('*').eq('id', jug_id).execute()
                    if jug_response.data:
                        jugadores.append(jug_response.data[0])
                except:
                    continue
            
            return [jug.get('nombre', f'Jugador {jug_id}') for jug in jugadores]
        except Exception as e:
            print(f"Error getting jugadores: {e}")
            return []
    
    def get_estadisticas_jugadores(self, equipo=None, jugador=None):
        """Obtiene estadísticas de jugadores sin filtro de fechas"""
        try:
            query = self.client.table('jugadores_partido').select('*')
            
            # JOIN con jugadores para obtener nombres
            query = query.select(
                '*, jugadores!inner(nombre)'
            )
            
            # JOIN con equipos para obtener nombres
            query = query.select(
                '*, equipos!inner(nombre)'
            )
            
            if equipo and equipo != "Todos":
                query = query.eq('equipo_nombre', equipo)
            
            if jugador and jugador != "Todos":
                query = query.eq('jugadores.nombre', jugador)
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Renombrar columnas del JOIN
                if 'jugadores' in df.columns:
                    df['nombre_jugador'] = df['jugadores'].apply(lambda x: x.get('nombre', '') if isinstance(x, dict) else '')
                    df.drop('jugadores', axis=1, inplace=True)
                
                if 'equipos' in df.columns:
                    df['equipo_nombre'] = df['equipos'].apply(lambda x: x.get('nombre', '') if isinstance(x, dict) else '')
                    df.drop('equipos', axis=1, inplace=True)
                
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas jugadores: {e}")
            return pd.DataFrame()
    
    def get_partidos(self):
        """Obtiene todos los partidos"""
        try:
            response = self.client.table('partidos').select('*').execute()
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting partidos: {e}")
            return pd.DataFrame()
    
    def get_tiros(self, equipo=None, jugador=None):
        """Obtiene datos de tiros"""
        try:
            query = self.client.table('tiros').select('*')
            
            if equipo and equipo != "Todos":
                # Necesitaríamos JOIN con equipos
                query = query.eq('equipo_nombre', equipo)
            
            if jugador and jugador != "Todos":
                query = query.eq('jugador_nombre', jugador)
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting tiros: {e}")
            return pd.DataFrame()
    
    def get_estadisticas_agregadas(self, equipo=None):
        """Obtiene estadísticas agregadas por equipo"""
        try:
            query = self.client.table('jugadores_partido').select('*')
            
            # JOIN con equipos
            query = query.select(
                '*, equipos!inner(nombre)'
            )
            
            if equipo and equipo != "Todos":
                query = query.eq('equipos.nombre', equipo)
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Renombrar columna de equipo
                if 'equipos' in df.columns:
                    df['equipo_nombre'] = df['equipos'].apply(lambda x: x.get('nombre', '') if isinstance(x, dict) else '')
                    df.drop('equipos', axis=1, inplace=True)
                
                # Agrupar por equipo
                if not df.empty and 'equipo_nombre' in df.columns:
                    stats = df.groupby('equipo_nombre').agg({
                        'puntos': 'mean',
                        'rebotes_tot': 'mean',
                        'asistencias': 'mean',
                        'robos': 'mean',
                        'tapones_favor': 'mean',
                        'valoracion': 'mean',
                        't2_anotados': 'sum',
                        't2_intentados': 'sum',
                        't3_anotados': 'sum',
                        't3_intentados': 'sum',
                        'tl_anotados': 'sum',
                        'tl_intentados': 'sum'
                    }).reset_index()
                    
                    return stats
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas agregadas: {e}")
            return pd.DataFrame()
    
    def get_estadisticas_mensuales(self, equipo=None):
        """Obtiene estadísticas mensuales"""
        try:
            query = self.client.table('jugadores_partido').select('*')
            
            if equipo and equipo != "Todos":
                query = query.eq('equipo_nombre', equipo)
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                if not df.empty and 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['mes'] = df['created_at'].dt.to_period('M')
                    
                    stats = df.groupby('mes').agg({
                        'puntos': 'mean',
                        'rebotes_tot': 'mean',
                        'asistencias': 'mean',
                        'valoracion': 'mean'
                    }).reset_index()
                    
                    stats['mes'] = stats['mes'].astype(str)
                    return stats
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas mensuales: {e}")
            return pd.DataFrame()
    
    def get_estadisticas_parejas(self, equipo=None):
        """Obtiene estadísticas de parejas de jugadores"""
        try:
            # Esta es una consulta compleja que necesitaría análisis de play-by-play
            # Por ahora, devolvemos un DataFrame vacío como placeholder
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas parejas: {e}")
            return pd.DataFrame()
    
    def get_estadisticas_por_posicion(self, posicion=None):
        """Obtiene estadísticas agrupadas por posición"""
        try:
            # Necesitaríamos JOIN con tabla de jugadores que tenga posición
            # Por ahora, agrupamos por dorsal como placeholder
            query = self.client.table('jugadores_partido').select('*')
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                if not df.empty and 'dorsal' in df.columns:
                    stats = df.groupby('dorsal').agg({
                        'puntos': 'mean',
                        'rebotes_tot': 'mean',
                        'asistencias': 'mean',
                        'valoracion': 'mean'
                    }).reset_index()
                    
                    return stats
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas por posición: {e}")
            return pd.DataFrame()
    
    def get_rachas_equipo(self, equipo=None):
        """Obtiene rachas de victorias/derrotas por equipo"""
        try:
            query = self.client.table('jugadores_partido').select('*')
            
            if equipo and equipo != "Todos":
                query = query.eq('equipo_nombre', equipo)
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                if not df.empty and 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df = df.sort_values('created_at')
                    
                    # Calcular victorias basadas en plus_minus
                    df['victoria'] = df['plus_minus'] > 0
                    
                    # Calcular rachas
                    rachas = []
                    racha_actual = 0
                    racha_max = 0
                    
                    for _, row in df.iterrows():
                        if row['victoria']:
                            if racha_actual >= 0:
                                racha_actual += 1
                            else:
                                racha_actual = 1
                        else:
                            if racha_actual <= 0:
                                racha_actual -= 1
                            else:
                                racha_actual = -1
                        
                        racha_max = max(racha_max, abs(racha_actual))
                    
                    return {
                        'racha_actual': racha_actual,
                        'racha_max': racha_max,
                        'total_victorias': len(df[df['victoria']]),
                        'total_derrotas': len(df[~df['victoria']])
                    }
            return {}
        except Exception as e:
            print(f"Error getting rachas equipo: {e}")
            return {}
    
    def get_matchups(self, equipo1=None, equipo2=None):
        """Obtiene estadísticas de enfrentamientos entre equipos"""
        try:
            # Esta consulta necesitaría análisis de partidos entre equipos específicos
            # Por ahora, devolvemos un DataFrame vacío como placeholder
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting matchups: {e}")
            return pd.DataFrame()
    
    def get_estadisticas_clutch(self, minutos_restantes=5):
        """Obtiene estadísticas en momentos clave"""
        try:
            # Esta consulta necesitaría análisis de play-by-play
            # Por ahora, filtramos por partidos donde el jugador jugó muchos minutos
            query = self.client.table('jugadores_partido').select('*').gte('minutos', 30)
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error getting estadísticas clutch: {e}")
            return pd.DataFrame()
