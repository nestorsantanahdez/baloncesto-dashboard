import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.stats_calculator import StatsCalculator
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers, FilterHelpers

class PlayerAnalysisModule:
    """Módulo de análisis individual de jugadores"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de análisis de jugadores"""
        st.header("👤 Análisis Individual de Jugadores")
        
        # Filtros principales
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            jugadores = db_manager.get_jugadores()
            jugadores.insert(0, "Todos")
            jugador_seleccionado = st.selectbox("Seleccionar Jugador", jugadores)
        
        with col2:
            posiciones = ["Todas", "Base", "Escolta", "Alero", "Ala-Pívot", "Pívot"]
            posicion_seleccionada = st.selectbox("Filtrar por Posición", posiciones)
        
        with col3:
            min_edad, max_edad = st.slider(
                "Rango de Edad",
                min_value=18, max_value=45, value=(18, 45)
            )
        
        # Filtros adicionales
        with st.expander("🎛️ Filtros Avanzados"):
            col1, col2 = st.columns(2)
            
            with col1:
                min_puntos = st.number_input("Mínimo Puntos por Partido", value=0)
                min_valoracion = st.number_input("Mínimo Valoración", value=0)
            
            with col2:
                min_minutos = st.number_input("Mínimo Minutos", value=0)
                ordenar_por = st.selectbox(
                    "Ordenar por",
                    ["valoracion", "puntos", "rebotes_tot", "asistencias", "per"]
                )
        
        # Obtener datos
        df_jugadores = db_manager.get_estadisticas_jugadores()
        
        if df_jugadores.empty:
            st.warning("No hay datos disponibles para el análisis")
            return
        
        # Aplicar filtros
        df_filtrado = df_jugadores.copy()
        
        # Filtro por jugador
        if jugador_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['nombre_jugador'] == jugador_seleccionado]
        
        # Filtro por posición (simulado - necesitaría columna posición)
        if posicion_seleccionada != "Todas":
            # Por ahora, usamos dorsal como placeholder de posición
            posicion_map = {
                "Base": [1, 2, 3],
                "Escolta": [4, 5, 6],
                "Alero": [7, 8, 9],
                "Ala-Pívot": [10, 11],
                "Pívot": [12, 13, 14, 15]
            }
            
            if posicion_seleccionada in posicion_map:
                df_filtrado = df_filtrado[df_filtrado['dorsal'].isin(posicion_map[posicion_seleccionada])]
        
        # Filtro por edad (simulado - necesitaría columna edad)
        # Por ahora, no aplicamos filtro de edad
        
        # Filtros estadísticos
        if min_puntos > 0:
            df_filtrado = df_filtrado[df_filtrado['puntos'] >= min_puntos]
        
        if min_valoracion > 0:
            df_filtrado = df_filtrado[df_filtrado['valoracion'] >= min_valoracion]
        
        if min_minutos > 0:
            df_filtrado = df_filtrado[df_filtrado['minutos'] >= min_minutos]
        
        # Ordenar
        if ordenar_por in df_filtrado.columns:
            df_filtrado = df_filtrado.sort_values(ordenar_por, ascending=False)
        
        if df_filtrado.empty:
            st.warning("No hay jugadores que cumplan con los filtros seleccionados")
            return
        
        # Mostrar resultados
        PlayerAnalysisModule._render_player_stats(df_filtrado, jugador_seleccionado)
        PlayerAnalysisModule._render_advanced_analysis(df_filtrado)
        PlayerAnalysisModule._render_performance_trends(df_filtrado)
        PlayerAnalysisModule._render_clutch_analysis(df_filtrado)
    
    @staticmethod
    def _render_player_stats(df, jugador_seleccionado):
        """Renderiza estadísticas de jugadores"""
        st.subheader("📊 Estadísticas de Jugadores")
        
        if jugador_seleccionado != "Todos":
            # Vista detallada de un jugador
            df_jugador = df[df['nombre_jugador'] == jugador_seleccionado]
            
            if not df_jugador.empty:
                st.write(f"### 🏀 {jugador_seleccionado}")
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Puntos Promedio",
                        f"{df_jugador['puntos'].mean():.1f}"
                    )
                
                with col2:
                    st.metric(
                        "Rebotes Promedio",
                        f"{df_jugador['rebotes_tot'].mean():.1f}"
                    )
                
                with col3:
                    st.metric(
                        "Asistencias Promedio",
                        f"{df_jugador['asistencias'].mean():.1f}"
                    )
                
                with col4:
                    st.metric(
                        "Valoración Promedio",
                        f"{df_jugador['valoracion'].mean():.1f}"
                    )
                
                # Estadísticas avanzadas
                st.subheader("📈 Estadísticas Avanzadas")
                advanced_stats = StatsCalculator.calculate_advanced_stats(df_jugador)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Eficiencia**")
                    st.write(f"- **PER**: {advanced_stats.get('PER', 0)}")
                    st.write(f"- **TS%**: {advanced_stats.get('TS%', 0)}%")
                    st.write(f"- **ORtg**: {advanced_stats.get('ORtg', 0)}")
                
                with col2:
                    st.write(**Estilo de Juego**")
                    st.write(f"- **PACE**: {advanced_stats.get('PACE', 0)}")
                    st.write(f"- **USG%**: {advanced_stats.get('USG%', 0)}%")
                    st.write(f"- **AST/TOV**: {advanced_stats.get('AST/TOV', 0)}")
                
                # Historial reciente
                st.subheader("📅 Rendimiento Reciente")
                df_reciente = df_jugador.sort_values('created_at', ascending=False).head(10)
                
                columnas_mostrar = [
                    'created_at', 'puntos', 'rebotes_tot', 'asistencias', 
                    'valoracion', 'minutos'
                ]
                
                df_display = df_reciente[columnas_mostrar].copy()
                df_display.columns = [
                    'Fecha', 'PTS', 'REB', 'AST', 'VAL', 'MIN'
                ]
                
                st.dataframe(df_display, use_container_width=True)
        
        else:
            # Vista de todos los jugadores
            st.write("### 📋 Tabla General de Jugadores")
            
            # Estadísticas agregadas por jugador
            df_agregado = df.groupby('nombre_jugador').agg({
                'puntos': 'mean',
                'rebotes_tot': 'mean',
                'asistencias': 'mean',
                'valoracion': 'mean',
                'minutos': 'mean',
                'partidos': 'count'
            }).reset_index()
            
            # Calcular PER individual
            df_agregado['per'] = (
                (df_agregado['puntos'] + df_agregado['rebotes_tot'] + 
                 df_agregado['asistencias'] + df_agregado['robos'].mean() + 
                 df_agregado['tapones_favor'].mean() - df_agregado['perdidas'].mean() - 
                 df_agregado['faltas_com'].mean()) / df_agregado['minutos'] * 40
            ).fillna(0)
            
            # Tabla ordenable
            columnas_mostrar = [
                'nombre_jugador', 'puntos', 'rebotes_tot', 'asistencias',
                'valoracion', 'per', 'minutos', 'partidos'
            ]
            
            df_display = df_agregado[columnas_mostrar].copy()
            df_display.columns = [
                'Jugador', 'PTS', 'REB', 'AST', 'VAL', 'PER', 'MIN', 'PJ'
            ]
            
            # Resaltar mejores valores
            df_display = DataHelpers.highlight_best_values(
                df_display,
                ['PTS', 'REB', 'AST', 'VAL', 'PER']
            )
            
            st.dataframe(df_display, use_container_width=True)
            
            # Top performers
            st.subheader("🏆 Top Performers")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                top_scorer = df_agregado.loc[df_agregado['puntos'].idxmax()]
                st.metric(
                    "Máximo Anotador",
                    top_scorer['nombre_jugador'],
                    f"{top_scorer['puntos']:.1f} pts"
                )
            
            with col2:
                top_rebounder = df_agregado.loc[df_agregado['rebotes_tot'].idxmax()]
                st.metric(
                    "Máximo Rebotador",
                    top_rebounder['nombre_jugador'],
                    f"{top_rebounder['rebotes_tot']:.1f} reb"
                )
            
            with col3:
                top_assister = df_agregado.loc[df_agregado['asistencias'].idxmax()]
                st.metric(
                    "Máximo Asistente",
                    top_assister['nombre_jugador'],
                    f"{top_assister['asistencias']:.1f} ast"
                )
    
    @staticmethod
    def _render_advanced_analysis(df):
        """Renderiza análisis avanzado de jugadores"""
        st.subheader("🔬 Análisis Avanzado")
        
        # Distribución por rendimiento
        st.write("### 📊 Distribución por Nivel de Rendimiento")
        
        df_agregado = df.groupby('nombre_jugador').agg({
            'valoracion': 'mean'
        }).reset_index()
        
        # Clasificar jugadores por rendimiento
        def clasificar_rendimiento(val):
            if pd.isna(val):
                return "Sin Datos"
            elif val >= 25:
                return "Excelente"
            elif val >= 15:
                return "Muy Bueno"
            elif val >= 5:
                return "Bueno"
            else:
                return "Regular"
        
        df_agregado['nivel_rendimiento'] = df_agregado['valoracion'].apply(clasificar_rendimiento)
        
        # Gráfico de distribución
        fig_distribucion = px.pie(
            df_agregado['nivel_rendimiento'].value_counts(),
            values=df_agregado['nivel_rendimiento'].value_counts().values,
            names=df_agregado['nivel_rendimiento'].value_counts().index,
            title="Distribución de Jugadores por Rendimiento"
        )
        
        st.plotly_chart(fig_distribucion, use_container_width=True)
        
        # Correlación entre estadísticas
        st.write("### 🔗 Correlación entre Estadísticas")
        
        df_corr = df_agregado[['puntos', 'rebotes_tot', 'asistencias', 'valoracion']].corr()
        
        fig_corr = px.imshow(
            df_corr,
            title="Matriz de Correlación",
            color_continuous_scale='RdBu',
            labels=dict(x="Estadística", y="Estadística", color="Correlación")
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Análisis de consistencia
        st.write("### 📈 Análisis de Consistencia")
        
        consistencia_data = []
        for jugador in df_agregado['nombre_jugador'].unique():
            df_jugador = df[df['nombre_jugador'] == jugador]
            if not df_jugador.empty:
                consistencia = DataHelpers.calculate_team_consistency(df_jugador)
                consistencia_data.append({
                    'jugador': jugador,
                    'consistencia': consistencia,
                    'valoracion_media': df_jugador['valoracion'].mean(),
                    'desviacion': df_jugador['valoracion'].std()
                })
        
        df_consistencia = pd.DataFrame(consistencia_data)
        df_consistencia = df_consistencia.sort_values('consistencia', ascending=False)
        
        fig_consistencia = px.bar(
            df_consistencia.head(10),
            x='jugador',
            y='consistencia',
            title="Top 10 Jugadores más Consistentes",
            labels={'consistencia': 'Consistencia (%)', 'jugador': 'Jugador'}
        )
        
        st.plotly_chart(fig_consistencia, use_container_width=True)
    
    @staticmethod
    def _render_performance_trends(df):
        """Renderiza tendencias de rendimiento"""
        st.subheader("📈 Tendencias de Rendimiento")
        
        if df.empty or 'created_at' not in df.columns:
            return
        
        # Evolución temporal de jugadores destacados
        df_top_players = df.groupby('nombre_jugador')['valoracion'].mean().nlargest(5).index
        
        fig_tendencia = go.Figure()
        
        for jugador in df_top_players:
            df_jugador = df[df['nombre_jugador'] == jugador].sort_values('created_at')
            
            if not df_jugador.empty:
                # Media móvil de 3 partidos
                df_jugador['valoracion_suavizada'] = df_jugador['valoracion'].rolling(window=3).mean()
                
                fig_tendencia.add_trace(go.Scatter(
                    x=df_jugador['created_at'],
                    y=df_jugador['valoracion_suavizada'],
                    mode='lines',
                    name=jugador,
                    line=dict(width=2)
                ))
        
        fig_tendencia.update_layout(
            title="Evolución de Valoración - Top 5 Jugadores",
            xaxis_title="Fecha",
            yaxis_title="Valoración (Media Móvil 3 partidos)",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_tendencia, use_container_width=True)
    
    @staticmethod
    def _render_clutch_analysis(df):
        """Renderiza análisis de momentos clave"""
        st.subheader("⏰ Análisis de Momentos Clave (Clutch)")
        
        # Definir partidos clutch (jugador jugó más de 30 minutos)
        df_clutch = df[df['minutos'] >= 30]
        
        if df_clutch.empty:
            st.info("No hay suficientes datos para análisis clutch")
            return
        
        # Estadísticas en momentos clutch
        clutch_stats = df_clutch.groupby('nombre_jugador').agg({
            'puntos': 'mean',
            'rebotes_tot': 'mean',
            'asistencias': 'mean',
            'valoracion': 'mean',
            'plus_minus': 'mean',
            'partidos_clutch': 'count'
        }).reset_index()
        
        # Comparar con estadísticas generales
        general_stats = df.groupby('nombre_jugador').agg({
            'puntos_general': 'mean',
            'valoracion_general': 'mean'
        }).reset_index()
        
        # Combinar estadísticas
        df_comparison = pd.merge(clutch_stats, general_stats, on='nombre_jugador', how='inner')
        
        # Calcular mejora en clutch
        df_comparison['mejora_puntos'] = (
            (df_comparison['puntos'] - df_comparison['puntos_general']) / 
            df_comparison['puntos_general'] * 100
        ).fillna(0)
        
        df_comparison['mejora_valoracion'] = (
            (df_comparison['valoracion'] - df_comparison['valoracion_general']) / 
            df_comparison['valoracion_general'] * 100
        ).fillna(0)
        
        # Mostrar jugadores clutch
        st.write("### 🏆 Mejores Jugadores en Momentos Clave")
        
        df_clutch_top = df_comparison[
            df_comparison['partidos_clutch'] >= 5  # Mínimo 5 partidos clutch
        ].sort_values('valoracion', ascending=False).head(10)
        
        if not df_clutch_top.empty:
            columnas_mostrar = [
                'nombre_jugador', 'puntos', 'valoracion', 'mejora_puntos',
                'mejora_valoracion', 'partidos_clutch'
            ]
            
            df_display = df_clutch_top[columnas_mostrar].copy()
            df_display.columns = [
                'Jugador', 'PTS Clutch', 'VAL Clutch', '% Mejora PTS',
                '% Mejora VAL', 'Partidos Clutch'
            ]
            
            st.dataframe(df_display, use_container_width=True)
            
            # Gráfico de mejora en clutch
            fig_mejora = px.scatter(
                df_clutch_top,
                x='puntos_general',
                y='puntos',
                size='mejora_puntos',
                color='mejora_valoracion',
                title="Rendimiento General vs Clutch",
                labels={
                    'puntos_general': 'Puntos Promedio General',
                    'puntos': 'Puntos Promedio Clutch',
                    'mejora_puntos': 'Mejora (%)',
                    'mejora_valoracion': 'Mejora Valoración (%)'
                },
                hover_data=['nombre_jugador']
            )
            
            # Línea de igualdad
            fig_mejora.add_trace(go.Scatter(
                x=[0, df_clutch_top['puntos_general'].max()],
                y=[0, df_clutch_top['puntos_general'].max()],
                mode='lines',
                name='Igualdad',
                line=dict(dash='dash', color='gray')
            ))
            
            st.plotly_chart(fig_mejora, use_container_width=True)
