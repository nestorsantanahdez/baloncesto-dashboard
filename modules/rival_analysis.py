import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class RivalAnalysisModule:
    """Módulo de análisis de rivales y matchups"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de análisis de rivales"""
        st.header("🏆 Análisis de Rivales y Matchups")
        
        # Tipo de análisis
        tipo_analisis = st.radio(
            "Tipo de Análisis",
            ["Matchups entre Equipos", "Impacto de Jugadores vs Rivales", "Análisis de Rivalidades", "Predicciones de Enfrentamientos"]
        )
        
        if tipo_analisis == "Matchups entre Equipos":
            RivalAnalysisModule._render_team_matchups(db_manager)
        elif tipo_analisis == "Impacto de Jugadores vs Rivales":
            RivalAnalysisModule._render_player_rival_impact(db_manager)
        elif tipo_analisis == "Análisis de Rivalidades":
            RivalAnalysisModule._render_rivalry_analysis(db_manager)
        elif tipo_analisis == "Predicciones de Enfrentamientos":
            RivalAnalysisModule._render_matchup_predictions(db_manager)
    
    @staticmethod
    def _render_team_matchups(db_manager):
        """Renderiza análisis de matchups entre equipos"""
        st.subheader("⚔️ Matchups entre Equipos")
        
        # Selección de equipos
        col1, col2 = st.columns(2)
        
        with col1:
            equipos = db_manager.get_equipos()
            equipo1 = st.selectbox("Equipo 1", equipos)
        
        with col2:
            equipos = db_manager.get_equipos()
            equipo2 = st.selectbox("Equipo 2", equipos, index=1 if len(equipos) > 1 else 0)
        
        if equipo1 == equipo2:
            st.warning("Selecciona equipos diferentes para analizar matchups")
            return
        
        # Obtener datos simulados de matchups
        df_matchups = RivalAnalysisModule._get_simulated_matchups(db_manager, equipo1, equipo2)
        
        if df_matchups.empty:
            st.warning("No hay datos suficientes para analizar matchups")
            return
        
        # Estadísticas head-to-head
        st.write(f"### 📊 Historial: {equipo1} vs {equipo2}")
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        partidos_jugados = len(df_matchups)
        victorias_eq1 = len(df_matchups[df_matchups['ganador'] == equipo1])
        victorias_eq2 = len(df_matchups[df_matchups['ganador'] == equipo2])
        
        with col1:
            st.metric("Partidos Jugados", partidos_jugados)
        
        with col2:
            st.metric(f"Victorias {equipo1}", victorias_eq1)
        
        with col3:
            st.metric(f"Victorias {equipo2}", victorias_eq2)
        
        with col4:
            porcentaje_eq1 = (victorias_eq1 / partidos_jugados * 100) if partidos_jugados > 0 else 0
            st.metric(f"% Victorias {equipo1}", f"{porcentaje_eq1:.1f}%")
        
        # Gráfico de evolución del enfrentamiento
        st.subheader("📈 Evolución del Enfrentamiento")
        
        fig_evolucion = px.line(
            df_matchups,
            x='partido_numero',
            y=['puntos_eq1', 'puntos_eq2'],
            title=f"Evolución de Puntos: {equipo1} vs {equipo2}",
            labels={
                'value': 'Puntos',
                'variable': 'Equipo',
                'partido_numero': 'Partido'
            },
            color_discrete_map={equipo1: 'blue', equipo2: 'red'}
        )
        
        st.plotly_chart(fig_evolucion, use_container_width=True)
        
        # Estadísticas detalladas
        st.subheader("📋 Estadísticas Detalladas")
        
        stats_comparison = pd.DataFrame({
            'Estadística': [
                'Puntos Promedio', 'Rebotes Promedio', 'Asistencias Promedio',
                'Victorias', 'Eficiencia Ofensiva'
            ],
            equipo1: [
                df_matchups['puntos_eq1'].mean(),
                df_matchups['rebotes_eq1'].mean(),
                df_matchups['asistencias_eq1'].mean(),
                victorias_eq1,
                (df_matchups['puntos_eq1'].mean() / 100) * 50  # Eficiencia simulada
            ],
            equipo2: [
                df_matchups['puntos_eq2'].mean(),
                df_matchups['rebotes_eq2'].mean(),
                df_matchups['asistencias_eq2'].mean(),
                victorias_eq2,
                (df_matchups['puntos_eq2'].mean() / 100) * 50  # Eficiencia simulada
            ]
        })
        
        fig_comparison = px.bar(
            stats_comparison.melt(id_vars=['Estadística'], var_name='variable', value_name='valor'),
            x='Estadística',
            y='valor',
            color='variable',
            title=f"Comparación de Estadísticas: {equipo1} vs {equipo2}",
            barmode='group'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    @staticmethod
    def _render_player_rival_impact(db_manager):
        """Renderiza análisis de impacto de jugadores contra rivales específicos"""
        st.subheader("🎯 Impacto de Jugadores vs Rivales")
        
        # Selección de jugador y rival
        col1, col2 = st.columns(2)
        
        with col1:
            jugadores = db_manager.get_jugadores()
            jugador_seleccionado = st.selectbox("Jugador", jugadores)
        
        with col2:
            equipos = db_manager.get_equipos()
            rival_seleccionado = st.selectbox("Equipo Rival", equipos)
        
        # Obtener datos simulados
        df_impact = RivalAnalysisModule._get_player_rival_stats(db_manager, jugador_seleccionado, rival_seleccionado)
        
        if df_impact.empty:
            st.warning("No hay datos suficientes para el análisis")
            return
        
        # Estadísticas del jugador contra el rival
        st.write(f"### 📊 {jugador_seleccionado} vs {rival_seleccionado}")
        
        # Métricas clave
        col1, col2, col3 = st.columns(3)
        
        partidos_vs_rival = len(df_impact)
        puntos_promedio = df_impact['puntos'].mean()
        valoracion_promedio = df_impact['valoracion'].mean()
        
        with col1:
            st.metric("Partidos vs Rival", partidos_vs_rival)
        
        with col2:
            st.metric("Puntos Promedio", f"{puntos_promedio:.1f}")
        
        with col3:
            st.metric("Valoración Promedio", f"{valoracion_promedio:.1f}")
        
        # Comparación con rendimiento general
        df_general = db_manager.get_estadisticas_jugadores()
        
        if not df_general.empty:
            df_jugador_general = df_general[df_general['nombre_jugador'] == jugador_seleccionado]
            
            if not df_jugador_general.empty:
                puntos_general = df_jugador_general['puntos'].mean()
                valoracion_general = df_jugador_general['valoracion'].mean()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    mejora_puntos = ((puntos_promedio - puntos_general) / puntos_general * 100) if puntos_general > 0 else 0
                    st.metric("Mejora vs Rival (%)", f"{mejora_puntos:+.1f}%")
                
                with col2:
                    mejora_valoracion = ((valoracion_promedio - valoracion_general) / valoracion_general * 100) if valoracion_general > 0 else 0
                    st.metric("Mejora Valoración (%)", f"{mejora_valoracion:+.1f}%")
        
        # Histórico de enfrentamientos
        st.subheader("📅 Histórico de Enfrentamientos")
        
        if 'fecha' in df_impact.columns:
            df_impact_sorted = df_impact.sort_values('fecha')
            
            fig_historico = px.scatter(
                df_impact_sorted,
                x='fecha',
                y='valoracion',
                size='puntos',
                title=f"Evolución de {jugador_seleccionado} vs {rival_seleccionado}",
                labels={
                    'valoracion': 'Valoración',
                    'fecha': 'Fecha',
                    'puntos': 'Puntos'
                }
            )
            
            st.plotly_chart(fig_historico, use_container_width=True)
            
            # Tabla de enfrentamientos
            columnas_mostrar = ['fecha', 'puntos', 'rebotes_tot', 'asistencias', 'valoracion']
            df_display = df_impact_sorted[columnas_mostrar].copy()
            df_display.columns = ['Fecha', 'PTS', 'REB', 'AST', 'VAL']
            
            st.dataframe(df_display, use_container_width=True)
    
    @staticmethod
    def _render_rivalry_analysis(db_manager):
        """Renderiza análisis de rivalidades entre equipos"""
        st.subheader("🔥 Análisis de Rivalidades")
        
        # Análisis de las rivalidades más intensas
        equipos = db_manager.get_equipos()
        
        if len(equipos) < 2:
            st.warning("Se necesitan al menos 2 equipos para analizar rivalidades")
            return
        
        # Simular análisis de rivalidades
        rivalidades = []
        
        for i, eq1 in enumerate(equipos):
            for j, eq2 in enumerate(equipos):
                if i < j:
                    # Simular intensidad de rivalidad
                    df_matchups = RivalAnalysisModule._get_simulated_matchups(db_manager, eq1, eq2)
                    
                    if not df_matchups.empty:
                        partidos = len(df_matchups)
                        diferencia_puntos = abs(df_matchups['puntos_eq1'].mean() - df_matchups['puntos_eq2'].mean())
                        intensidad = (partidos * 0.3 + diferencia_puntos * 0.7) / 100
                        
                        rivalidades.append({
                            'rivalidad': f"{eq1} vs {eq2}",
                            'intensidad': intensidad,
                            'partidos': partidos,
                            'diferencia_puntos': diferencia_puntos
                        })
        
        if rivalidades:
            df_rivalidades = pd.DataFrame(rivalidades)
            df_rivalidades = df_rivalidades.sort_values('intensidad', ascending=False).head(10)
            
            # Gráfico de rivalidades
            fig_rivalidades = px.bar(
                df_rivalidades,
                x='rivalidad',
                y='intensidad',
                title="Top 10 Rivalidades Más Intensas",
                labels={
                    'intensidad': 'Intensidad de Rivalidad',
                    'rivalidad': 'Enfrentamiento'
                },
                color='intensidad',
                color_continuous_scale='Reds'
            )
            
            fig_rivalidades.update_xaxis(tickangle=45)
            st.plotly_chart(fig_rivalidades, use_container_width=True)
            
            # Tabla de rivalidades
            df_display = df_rivalidades.copy()
            df_display.columns = ['Rivalidad', 'Intensidad', 'Partidos', 'Diferencia Puntos']
            st.dataframe(df_display, use_container_width=True)
    
    @staticmethod
    def _render_matchup_predictions(db_manager):
        """Renderiza predicciones de enfrentamientos"""
        st.subheader("🎯 Predicciones de Enfrentamientos")
        
        # Selección de equipos para predicción
        col1, col2 = st.columns(2)
        
        with col1:
            equipos = db_manager.get_equipos()
            equipo_local = st.selectbox("Equipo Local", equipos)
        
        with col2:
            equipos = db_manager.get_equipos()
            equipo_visitante = st.selectbox("Equipo Visitante", equipos, index=1 if len(equipos) > 1 else 0)
        
        if equipo_local == equipo_visitante:
            st.warning("Selecciona equipos diferentes para la predicción")
            return
        
        # Obtener estadísticas de ambos equipos
        df_stats = db_manager.get_estadisticas_agregadas()
        
        if df_stats.empty:
            st.warning("No hay datos suficientes para predicción")
            return
        
        df_local = df_stats[df_stats['equipo_nombre'] == equipo_local]
        df_visitante = df_stats[df_stats['equipo_nombre'] == equipo_visitante]
        
        if df_local.empty or df_visitante.empty:
            st.warning("No hay datos para uno o ambos equipos")
            return
        
        # Calcular factores de predicción
        st.write(f"### 🏀 Predicción: {equipo_local} vs {equipo_visitante}")
        
        # Factor 1: Rendimiento ofensivo
        puntos_local = df_local['puntos'].iloc[0]
        puntos_visitante = df_visitante['puntos'].iloc[0]
        factor_ofensivo = puntos_local / (puntos_local + puntos_visitante)
        
        # Factor 2: Rendimiento defensivo (simulado con rebotes)
        rebotes_local = df_local['rebotes_tot'].iloc[0]
        rebotes_visitante = df_visitante['rebotes_tot'].iloc[0]
        factor_defensivo = rebotes_local / (rebotes_local + rebotes_visitante)
        
        # Factor 3: Experiencia (simulado con valoración)
        valoracion_local = df_local['valoracion'].iloc[0]
        valoracion_visitante = df_visitante['valoracion'].iloc[0]
        factor_experiencia = valoracion_local / (valoracion_local + valoracion_visitante)
        
        # Factor 4: Ventaja de local (simulado)
        factor_local = 0.1  # 10% ventaja local
        
        # Probabilidades finales
        prob_local = (factor_ofensivo * 0.4 + factor_defensivo * 0.3 + factor_experiencia * 0.2 + factor_local * 0.1) * 100
        prob_visitante = 100 - prob_local
        
        # Mostrar predicción
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(f"Probabilidad {equipo_local}", f"{prob_local:.1f}%")
        
        with col2:
            st.metric(f"Probabilidad {equipo_visitante}", f"{prob_visitante:.1f}%")
        
        # Factores detallados
        st.subheader("📊 Factores Considerados")
        
        factores_df = pd.DataFrame({
            'Factor': ['Rendimiento Ofensivo', 'Rendimiento Defensivo', 'Experiencia', 'Ventaja Local'],
            equipo_local: [
                f"{factor_ofensivo*100:.1f}%",
                f"{factor_defensivo*100:.1f}%",
                f"{factor_experiencia*100:.1f}%",
                f"{factor_local*100:.1f}%"
            ],
            equipo_visitante: [
                f"{(1-factor_ofensivo)*100:.1f}%",
                f"{(1-factor_defensivo)*100:.1f}%",
                f"{(1-factor_experiencia)*100:.1f}%",
                "0.0%"
            ]
        })
        
        fig_factores = px.bar(
            factores_df.melt(id_vars=['Factor'], var_name='Equipo', value_name='valor'),
            x='Factor',
            y='valor',
            color='Equipo',
            title="Factores de Predicción",
            labels={'valor': 'Porcentaje (%)', 'variable': 'Equipo'},
            barmode='group'
        )
        
        st.plotly_chart(fig_factores, use_container_width=True)
        
        # Predicción de resultado
        st.subheader("🎯 Predicción del Resultado")
        
        ganador_probable = equipo_local if prob_local > prob_visitante else equipo_visitante
        confianza = abs(prob_local - 50) * 2  # Confianza basada en lo equilibrado que esté el matchup
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Ganador Probable", ganador_probable)
        
        with col2:
            st.metric("Confianza", f"{confianza:.1f}%")
        
        st.info("⚠️ *Esta predicción es simulada basada en estadísticas históricas y no garantiza el resultado real*")
    
    @staticmethod
    def _get_simulated_matchups(db_manager, equipo1, equipo2):
        """Obtiene datos simulados de matchups entre dos equipos"""
        # Simular datos de enfrentamientos
        import random
        
        matchups = []
        num_partidos = random.randint(5, 15)  # Simular entre 5-15 partidos
        
        for i in range(num_partidos):
            # Simular estadísticas para ambos equipos
            puntos_eq1 = random.randint(70, 120)
            puntos_eq2 = random.randint(70, 120)
            rebotes_eq1 = random.randint(30, 60)
            rebotes_eq2 = random.randint(30, 60)
            asistencias_eq1 = random.randint(15, 35)
            asistencias_eq2 = random.randint(15, 35)
            
            # Determinar ganador
            ganador = equipo1 if puntos_eq1 > puntos_eq2 else equipo2
            
            matchups.append({
                'partido_numero': i + 1,
                'ganador': ganador,
                'puntos_eq1': puntos_eq1,
                'puntos_eq2': puntos_eq2,
                'rebotes_eq1': rebotes_eq1,
                'rebotes_eq2': rebotes_eq2,
                'asistencias_eq1': asistencias_eq1,
                'asistencias_eq2': asistencias_eq2
            })
        
        return pd.DataFrame(matchups)
    
    @staticmethod
    def _get_player_rival_stats(db_manager, jugador, rival):
        """Obtiene estadísticas simuladas de un jugador contra un rival"""
        # Simular datos de enfrentamientos
        import random
        
        stats = []
        num_partidos = random.randint(3, 10)  # Simular entre 3-10 partidos
        
        for i in range(num_partidos):
            stats.append({
                'fecha': f"2024-0{random.randint(1,9)}-{random.randint(1,28)}",
                'puntos': random.randint(10, 35),
                'rebotes_tot': random.randint(3, 15),
                'asistencias': random.randint(2, 12),
                'valoracion': random.randint(5, 30)
            })
        
        return pd.DataFrame(stats)
