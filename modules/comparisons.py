import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.stats_calculator import StatsCalculator
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class ComparisonsModule:
    """Módulo de comparativas entre equipos y jugadores"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de comparativas"""
        st.header("📊 Comparativas")
        
        # Tipo de comparación
        tipo_comparacion = st.radio(
            "Tipo de Comparación",
            ["Equipos vs Equipos", "Jugadores vs Jugadores", "Equipo vs Equipo"]
        )
        
        if tipo_comparacion == "Equipos vs Equipos":
            ComparisonsModule._render_team_comparisons(db_manager)
        elif tipo_comparacion == "Jugadores vs Jugadores":
            ComparisonsModule._render_player_comparisons(db_manager)
        elif tipo_comparacion == "Equipo vs Equipo":
            ComparisonsModule._render_head_to_head(db_manager)
    
    @staticmethod
    def _render_team_comparisons(db_manager):
        """Renderiza comparación entre múltiples equipos"""
        st.subheader("🏀 Comparación de Equipos")
        
        # Selección de equipos
        col1, col2 = st.columns(2)
        
        with col1:
            equipos = db_manager.get_equipos()
            equipos_seleccionados = st.multiselect(
                "Seleccionar Equipos a Comparar",
                equipos,
                default=equipos[:3] if len(equipos) >= 3 else equipos
            )
        
        with col2:
            metricas = st.multiselect(
                "Métricas a Comparar",
                ["puntos", "rebotes_tot", "asistencias", "valoracion", "per"],
                default=["puntos", "rebotes_tot", "asistencias", "valoracion"]
            )
        
        if len(equipos_seleccionados) < 2:
            st.warning("Selecciona al menos 2 equipos para comparar")
            return
        
        # Obtener datos de equipos
        df_stats = db_manager.get_estadisticas_agregadas()
        
        if df_stats.empty:
            st.warning("No hay datos disponibles para comparación")
            return
        
        # Filtrar equipos seleccionados
        df_comparacion = df_stats[df_stats['equipo_nombre'].isin(equipos_seleccionados)]
        
        if df_comparacion.empty:
            st.warning("No hay datos para los equipos seleccionados")
            return
        
        # Gráfico de barras comparativo
        fig_barras = ChartGenerator.create_comparison_bar_chart(
            df_comparacion,
            metricas,
            f"Comparación de Equipos - {', '.join(metricas)}"
        )
        
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
        
        # Gráfico de radar
        st.subheader("🕸️ Perfil Comparativo de Equipos")
        
        # Preparar datos para radar
        df_radar = df_comparacion.copy()
        
        # Normalizar métricas para radar (0-100)
        for metrica in metricas:
            if metrica in df_radar.columns:
                max_val = df_radar[metrica].max()
                min_val = df_radar[metrica].min()
                if max_val > min_val:
                    df_radar[metrica] = (
                        (df_radar[metrica] - min_val) / (max_val - min_val) * 100
                    )
        
        fig_radar = ChartGenerator.create_radar_chart(
            df_radar,
            metricas,
            f"Perfil Comparativo - {', '.join(equipos_seleccionados)}"
        )
        
        if fig_radar:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tabla comparativa detallada
        st.subheader("📋 Tabla Comparativa Detallada")
        
        # Calcular estadísticas avanzadas
        df_comparacion_avanzado = df_comparacion.copy()
        
        for equipo in df_comparacion_avanzado['equipo_nombre'].unique():
            df_equipo = df_comparacion[df_comparacion_avanzado['equipo_nombre'] == equipo]
            if not df_equipo.empty:
                advanced_stats = StatsCalculator.calculate_advanced_stats(df_equipo)
                for key, value in advanced_stats.items():
                    df_comparacion_avanzado.loc[
                        df_comparacion_avanzado['equipo_nombre'] == equipo, key
                    ] = value
        
        # Tabla final
        columnas_mostrar = ['equipo_nombre'] + metricas + [col for col in df_comparacion_avanzado.columns if col in ['PER', 'TS%', 'ORtg', 'USG%']]
        
        df_final = df_comparacion_avanzado[columnas_mostrar].copy()
        df_final.columns = (
            ['Equipo'] + [col.upper().replace('_', ' ') for col in metricas] + 
            [col for col in ['PER', 'TS%', 'ORtg', 'USG%'] if col in df_final.columns]
        )
        
        st.dataframe(df_final, use_container_width=True)
    
    @staticmethod
    def _render_player_comparisons(db_manager):
        """Renderiza comparación entre múltiples jugadores"""
        st.subheader("👤 Comparación de Jugadores")
        
        # Selección de jugadores
        col1, col2 = st.columns(2)
        
        with col1:
            jugadores = db_manager.get_jugadores()
            jugadores_seleccionados = st.multiselect(
                "Seleccionar Jugadores a Comparar",
                jugadores,
                default=jugadores[:3] if len(jugadores) >= 3 else jugadores
            )
        
        with col2:
            metricas = st.multiselect(
                "Métricas a Comparar",
                ["puntos", "rebotes_tot", "asistencias", "valoracion", "per", "minutos"],
                default=["puntos", "rebotes_tot", "asistencias", "valoracion"]
            )
        
        if len(jugadores_seleccionados) < 2:
            st.warning("Selecciona al menos 2 jugadores para comparar")
            return
        
        # Obtener datos de jugadores
        df_jugadores = db_manager.get_estadisticas_jugadores()
        
        if df_jugadores.empty:
            st.warning("No hay datos disponibles para comparación")
            return
        
        # Agrupar por jugador
        df_agregado = df_jugadores.groupby('nombre_jugador').agg({
            'puntos': 'mean',
            'rebotes_tot': 'mean',
            'asistencias': 'mean',
            'valoracion': 'mean',
            'minutos': 'mean',
            'partidos': 'count'
        }).reset_index()
        
        # Filtrar jugadores seleccionados
        df_comparacion = df_agregado[df_agregado['nombre_jugador'].isin(jugadores_seleccionados)]
        
        if df_comparacion.empty:
            st.warning("No hay datos para los jugadores seleccionados")
            return
        
        # Calcular PER individual
        df_comparacion['per'] = (
            (df_comparacion['puntos'] + df_comparacion['rebotes_tot'] + 
             df_comparacion['asistencias'] + df_comparacion['robos'].mean() + 
             df_comparacion['tapones_favor'].mean() - df_comparacion['perdidas'].mean() - 
             df_comparacion['faltas_com'].mean()) / df_comparacion['minutos'] * 40
        ).fillna(0)
        
        # Gráfico de barras comparativo
        fig_barras = ChartGenerator.create_comparison_bar_chart(
            df_comparacion,
            metricas,
            f"Comparación de Jugadores - {', '.join(metricas)}"
        )
        
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
        
        # Gráfico de radar
        st.subheader("🕸️ Perfil Comparativo de Jugadores")
        
        # Preparar datos para radar
        df_radar = df_comparacion.copy()
        
        # Normalizar métricas para radar
        for metrica in metricas:
            if metrica in df_radar.columns:
                max_val = df_radar[metrica].max()
                min_val = df_radar[metrica].min()
                if max_val > min_val:
                    df_radar[metrica] = (
                        (df_radar[metrica] - min_val) / (max_val - min_val) * 100
                    )
        
        fig_radar = ChartGenerator.create_radar_chart(
            df_radar,
            metricas,
            f"Perfil Comparativo - {', '.join(jugadores_seleccionados)}"
        )
        
        if fig_radar:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Análisis de fortalezas y debilidades
        st.subheader("📈 Análisis de Fortalezas y Debilidades")
        
        for jugador in jugadores_seleccionados:
            df_jugador = df_comparacion[df_comparacion['nombre_jugador'] == jugador]
            
            if not df_jugador.empty:
                st.write(f"#### 🏀 {jugador}")
                
                # Fortalezas (métricas por encima del promedio)
                fortalezas = []
                debilidades = []
                
                for metrica in metricas:
                    if metrica in df_jugador.columns:
                        promedio_general = df_comparacion[metrica].mean()
                        valor_jugador = df_jugador[metrica].iloc[0]
                        
                        if valor_jugador > promedio_general:
                            fortalezas.append(f"{metrica}: {valor_jugador:.1f} (+{valor_jugador - promedio_general:+.1f})")
                        else:
                            debilidades.append(f"{metrica}: {valor_jugador:.1f} ({valor_jugador - promedio_general:+.1f})")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if fortalezas:
                        st.write("**🔥 Fortalezas:**")
                        for fortaleza in fortalezas:
                            st.write(f"- {fortaleza}")
                
                with col2:
                    if debilidades:
                        st.write("**⚠️ Debilidades:**")
                        for debilidad in debilidades:
                            st.write(f"- {debilidad}")
    
    @staticmethod
    def _render_head_to_head(db_manager):
        """Renderiza comparación directa entre dos equipos"""
        st.subheader("⚔️ Head-to-Head: Equipo vs Equipo")
        
        # Selección de equipos
        col1, col2 = st.columns(2)
        
        with col1:
            equipos = db_manager.get_equipos()
            equipo1 = st.selectbox("Equipo Local", equipos)
        
        with col2:
            equipo2 = st.selectbox("Equipo Visitante", equipos, index=1 if len(equipos) > 1 else 0)
        
        if equipo1 == equipo2:
            st.warning("Selecciona equipos diferentes para comparar")
            return
        
        # Obtener datos de ambos equipos
        df_stats = db_manager.get_estadisticas_agregadas()
        
        if df_stats.empty:
            st.warning("No hay datos disponibles para comparación")
            return
        
        # Filtrar datos de ambos equipos
        df_equipo1 = df_stats[df_stats['equipo_nombre'] == equipo1]
        df_equipo2 = df_stats[df_stats['equipo_nombre'] == equipo2]
        
        if df_equipo1.empty or df_equipo2.empty:
            st.warning("No hay datos suficientes para uno o ambos equipos")
            return
        
        # Métricas comparativas
        st.write(f"### 🏀 {equipo1} vs {equipo2}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                f"Puntos {equipo1}",
                f"{df_equipo1['puntos'].iloc[0]:.1f}",
                delta=f"{df_equipo1['puntos'].iloc[0] - df_equipo2['puntos'].iloc[0]:+.1f}"
            )
        
        with col2:
            st.metric(
                f"Puntos {equipo2}",
                f"{df_equipo2['puntos'].iloc[0]:.1f}",
                delta=f"{df_equipo2['puntos'].iloc[0] - df_equipo1['puntos'].iloc[0]:+.1f}"
            )
        
        with col3:
            st.metric(
                f"Rebotes {equipo1}",
                f"{df_equipo1['rebotes_tot'].iloc[0]:.1f}",
                delta=f"{df_equipo1['rebotes_tot'].iloc[0] - df_equipo2['rebotes_tot'].iloc[0]:+.1f}"
            )
        
        with col4:
            st.metric(
                f"Rebotes {equipo2}",
                f"{df_equipo2['rebotes_tot'].iloc[0]:.1f}",
                delta=f"{df_equipo2['rebotes_tot'].iloc[0] - df_equipo1['rebotes_tot'].iloc[0]:+.1f}"
            )
        
        # Gráfico comparativo
        metricas_h2h = ['puntos', 'rebotes_tot', 'asistencias', 'valoracion']
        
        df_h2h = pd.DataFrame({
            'Métrica': metricas_h2h,
            equipo1: [df_equipo1[metrica].iloc[0] for metrica in metricas_h2h],
            equipo2: [df_equipo2[metrica].iloc[0] for metrica in metricas_h2h]
        })
        
        fig_h2h = px.bar(
            df_h2h.melt(id_vars=['Métrica'], var_name='Equipo', value_name='Valor'),
            x='Métrica',
            y='Valor',
            color='Equipo',
            title=f"Comparación Directa: {equipo1} vs {equipo2}",
            barmode='group'
        )
        
        st.plotly_chart(fig_h2h, use_container_width=True)
        
        # Análisis de ventajas
        st.subheader("📊 Análisis de Ventajas")
        
        ventajas_equipo1 = []
        ventajas_equipo2 = []
        
        for metrica in metricas_h2h:
            val1 = df_equipo1[metrica].iloc[0]
            val2 = df_equipo2[metrica].iloc[0]
            
            if val1 > val2:
                ventajas_equipo1.append(f"{metrica}: +{val1 - val2:.1f}")
            else:
                ventajas_equipo2.append(f"{metrica}: +{val2 - val1:.1f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if ventajas_equipo1:
                st.write(f"### 🔥 Ventajas de {equipo1}")
                for ventaja in ventajas_equipo1:
                    st.write(f"- {ventaja}")
        
        with col2:
            if ventajas_equipo2:
                st.write(f"### 🔥 Ventajas de {equipo2}")
                for ventaja in ventajas_equipo2:
                    st.write(f"- {ventaja}")
        
        # Predicción basada en estadísticas
        st.subheader("🎯 Predicción Basada en Estadísticas")
        
        # Calcular "puntuación de poder" simple
        poder_equipo1 = (
            df_equipo1['puntos'].iloc[0] * 0.4 +
            df_equipo1['rebotes_tot'].iloc[0] * 0.3 +
            df_equipo1['asistencias'].iloc[0] * 0.2 +
            df_equipo1['valoracion'].iloc[0] * 0.1
        )
        
        poder_equipo2 = (
            df_equipo2['puntos'].iloc[0] * 0.4 +
            df_equipo2['rebotes_tot'].iloc[0] * 0.3 +
            df_equipo2['asistencias'].iloc[0] * 0.2 +
            df_equipo2['valoracion'].iloc[0] * 0.1
        )
        
        total_poder = poder_equipo1 + poder_equipo2
        prob_equipo1 = poder_equipo1 / total_poder * 100
        prob_equipo2 = poder_equipo2 / total_poder * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                f"Probabilidad {equipo1}",
                f"{prob_equipo1:.1f}%",
                delta=f"{prob_equipo1 - 50:+.1f}%"
            )
        
        with col2:
            st.metric(
                f"Probabilidad {equipo2}",
                f"{prob_equipo2:.1f}%",
                delta=f"{prob_equipo2 - 50:+.1f}%"
            )
        
        st.info("⚠️ *Esta predicción es solo basada en estadísticas históricas y no garantiza el resultado real*")
