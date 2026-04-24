import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.stats_calculator import StatsCalculator
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class TeamStatsModule:
    """Módulo de estadísticas por equipo"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de estadísticas por equipo"""
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
        df_stats = db_manager.get_estadisticas_agregadas(equipo_seleccionado)
        
        if df_stats.empty:
            st.warning("No hay datos disponibles para el equipo seleccionado")
            return
        
        # Calcular estadísticas avanzadas
        if equipo_seleccionado == "Todos":
            # Mostrar todos los equipos
            st.subheader("📈 Estadísticas por Equipo")
            
            # Tabla ordenable
            df_display = df_stats.copy()
            
            # Añadir estadísticas avanzadas
            if not df_display.empty:
                advanced_stats = {}
                for equipo in df_display['equipo_nombre'].unique():
                    df_equipo = df_stats[df_stats['equipo_nombre'] == equipo]
                    advanced_stats[equipo] = StatsCalculator.calculate_advanced_stats(df_equipo)
                
                # Convertir a DataFrame
                df_advanced = pd.DataFrame.from_dict(advanced_stats, orient='index')
                df_display = pd.concat([df_display.set_index('equipo_nombre'), df_advanced], axis=1)
                df_display.reset_index(inplace=True)
            
            # Ordenar
            df_display = df_display.sort_values(ordenar_por, ascending=False)
            
            # Resaltar mejores valores
            df_display = DataHelpers.highlight_best_values(
                df_display, 
                [ordenar_por], 
                ascending=(ordenar_por not in ['per', 'valoracion'])
            )
            
            st.dataframe(df_display, use_container_width=True)
            
            # Gráfico comparativo
            st.subheader("📊 Comparación Visual")
            fig = ChartGenerator.create_comparison_bar_chart(
                df_stats,
                ['puntos', 'rebotes_tot', 'asistencias', 'valoracion'],
                "Comparación de Equipos - Estadísticas Principales"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de estadísticas avanzadas
            if not df_advanced.empty:
                fig_advanced = ChartGenerator.create_comparison_bar_chart(
                    df_advanced.reset_index().rename(columns={'index': 'equipo_nombre'}),
                    ['PER', 'TS%', 'ORtg', 'USG%'],
                    "Comparación de Equipos - Estadísticas Avanzadas"
                )
                if fig_advanced:
                    st.plotly_chart(fig_advanced, use_container_width=True)
        
        else:
            # Mostrar detalles del equipo seleccionado
            st.subheader(f"🏀 Detalles de {equipo_seleccionado}")
            
            df_equipo = df_stats[df_stats['equipo_nombre'] == equipo_seleccionado]
            
            if not df_equipo.empty:
                # Métricas clave
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Puntos por Partido",
                        f"{df_equipo['puntos'].iloc[0]:.1f}"
                    )
                
                with col2:
                    st.metric(
                        "Rebotes por Partido",
                        f"{df_equipo['rebotes_tot'].iloc[0]:.1f}"
                    )
                
                with col3:
                    st.metric(
                        "Asistencias por Partido",
                        f"{df_equipo['asistencias'].iloc[0]:.1f}"
                    )
                
                with col4:
                    st.metric(
                        "Valoración Media",
                        f"{df_equipo['valoracion'].iloc[0]:.1f}"
                    )
                
                # Estadísticas avanzadas del equipo
                st.subheader("📈 Estadísticas Avanzadas")
                advanced_stats = StatsCalculator.calculate_advanced_stats(df_equipo)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Eficiencia Ofensiva**")
                    st.write(f"- **PER**: {advanced_stats.get('PER', 0)}")
                    st.write(f"- **TS%**: {advanced_stats.get('TS%', 0)}%")
                    st.write(f"- **ORtg**: {advanced_stats.get('ORtg', 0)}")
                
                with col2:
                    st.write("**Estilo de Juego**")
                    st.write(f"- **PACE**: {advanced_stats.get('PACE', 0)}")
                    st.write(f"- **USG%**: {advanced_stats.get('USG%', 0)}%")
                    st.write(f"- **AST/TOV**: {advanced_stats.get('AST/TOV', 0)}")
                
                # Obtener jugadores individuales del equipo
                df_jugadores = db_manager.get_estadisticas_jugadores(equipo_seleccionado)
                
                if not df_jugadores.empty:
                    st.subheader("👥 Roster del Equipo")
                    
                    # Tabla de jugadores ordenable
                    df_jugadores_display = df_jugadores.copy()
                    
                    # Calcular PER individual
                    if not df_jugadores_display.empty:
                        df_jugadores_display['per'] = (
                            (df_jugadores_display['puntos'] + df_jugadores_display['rebotes_tot'] + 
                             df_jugadores_display['asistencias'] + df_jugadores_display['robos'] + 
                             df_jugadores_display['tapones_favor'] - df_jugadores_display['perdidas'] - 
                             df_jugadores_display['faltas_com']) / df_jugadores_display['minutos'] * 40
                        ).fillna(0)
                    
                    # Ordenar por la métrica seleccionada
                    df_jugadores_display = df_jugadores_display.sort_values(
                        ordenar_por, ascending=False
                    )
                    
                    # Resaltar mejores valores
                    df_jugadores_display = DataHelpers.highlight_best_values(
                        df_jugadores_display,
                        [ordenar_por],
                        ascending=(ordenar_por not in ['per', 'valoracion'])
                    )
                    
                    # Columnas a mostrar
                    columnas_mostrar = [
                        'nombre_jugador', 'puntos', 'rebotes_tot', 'asistencias',
                        'valoracion', 'per', 'minutos'
                    ]
                    
                    df_final = df_jugadores_display[columnas_mostrar]
                    df_final.columns = [
                        'Jugador', 'PTS', 'REB', 'AST', 'VAL', 'PER', 'MIN'
                    ]
                    
                    st.dataframe(df_final, use_container_width=True)
                    
                    # Gráfico de radar del equipo
                    st.subheader("🕸️ Perfil del Equipo")
                    
                    # Promedios del equipo
                    team_profile = {
                        'Ataque': df_equipo['puntos'].iloc[0] / 100,  # Normalizado
                        'Rebotes': df_equipo['rebotes_tot'].iloc[0] / 50,  # Normalizado
                        'Asistencias': df_equipo['asistencias'].iloc[0] / 30,  # Normalizado
                        'Defensa': df_equipo['robos'].iloc[0] / 10,  # Normalizado
                        'Eficiencia': advanced_stats.get('PER', 0) / 30  # Normalizado
                    }
                    
                    df_radar = pd.DataFrame([team_profile])
                    fig_radar = ChartGenerator.create_radar_chart(
                        df_radar,
                        list(team_profile.keys()),
                        f"Perfil de Juego - {equipo_seleccionado}"
                    )
                    
                    if fig_radar:
                        st.plotly_chart(fig_radar, use_container_width=True)
                
                # Análisis de consistencia
                st.subheader("📊 Análisis de Consistencia")
                
                consistencia = DataHelpers.calculate_team_consistency(df_jugadores)
                st.metric("Consistencia del Equipo", f"{consistencia}%")
                
                # Distribución de minutos
                if not df_jugadores.empty:
                    fig_minutos = ChartGenerator.create_box_plot(
                        df_jugadores,
                        'minutos',
                        'nombre_jugador',
                        "Distribución de Minutos por Jugador"
                    )
                    
                    if fig_minutos:
                        st.plotly_chart(fig_minutos, use_container_width=True)
