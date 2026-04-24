import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class PairAnalysisModule:
    """Módulo de análisis de parejas de jugadores"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de análisis de parejas"""
        st.header("👥 Análisis de Parejas")
        
        # Filtros
        col1, col2 = st.columns([2, 1])
        
        with col1:
            equipos = db_manager.get_equipos()
            equipos.insert(0, "Todos")
            equipo_seleccionado = st.selectbox("Seleccionar Equipo", equipos)
        
        with col2:
            tipo_analisis = st.selectbox(
                "Tipo de Análisis",
                ["Asistencias", "Rebotes", "Sinergia General", "Impacto en Victorias"]
            )
        
        # Obtener datos
        df_jugadores = db_manager.get_estadisticas_jugadores(equipo_seleccionado)
        
        if df_jugadores.empty:
            st.warning("No hay datos disponibles para el análisis de parejas")
            return
        
        if tipo_analisis == "Asistencias":
            PairAnalysisModule._render_asistencias_analysis(df_jugadores)
        elif tipo_analisis == "Rebotes":
            PairAnalysisModule._render_rebotes_analysis(df_jugadores)
        elif tipo_analisis == "Sinergia General":
            PairAnalysisModule._render_sinergia_analysis(df_jugadores)
        elif tipo_analisis == "Impacto en Victorias":
            PairAnalysisModule._render_impacto_analysis(df_jugadores)
    
    @staticmethod
    def _render_asistencias_analysis(df):
        """Renderiza análisis de asistencias entre jugadores"""
        st.subheader("🎯 Análisis de Asistencias")
        
        # Matriz de asistencias (simulada - necesitaría play-by-play real)
        jugadores = df['nombre_jugador'].unique()
        
        # Crear matriz simulada basada en asistencias totales
        matriz_asistencias = pd.DataFrame(
            index=jugadores,
            columns=jugadores,
            data=0
        )
        
        # Llenar diagonal con asistencias totales (placeholder)
        for jugador in jugadores:
            df_jugador = df[df['nombre_jugador'] == jugador]
            if not df_jugador.empty:
                matriz_asistencias.loc[jugador, jugador] = df_jugador['asistencias'].mean()
        
        # Añadir algunas asistencias cruzadas simuladas
        for i, jug1 in enumerate(jugadores):
            for j, jug2 in enumerate(jugadores):
                if i != j:
                    # Simular asistencias basadas en minutos jugados juntos
                    df_jug1 = df[df['nombre_jugador'] == jug1]
                    df_jug2 = df[df['nombre_jugador'] == jug2]
                    
                    if not df_jug1.empty and not df_jug2.empty:
                        min_comunes = min(df_jug1['minutos'].mean(), df_jug2['minutos'].mean())
                        matriz_asistencias.loc[jug1, jug2] = min_comunes * 0.1
        
        st.write("**Matriz de Asistencias entre Jugadores**")
        fig_heatmap = ChartGenerator.create_heatmap(
            matriz_asistencias,
            'columns',  # nombre de columna para jugadores que reciben
            'index',    # nombre de fila para jugadores que asisten
            'value',     # valores de asistencias
            "Asistencias entre Jugadores"
        )
        
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Top parejas de asistencias
        st.subheader("🏆 Mejores Parejas de Asistencia")
        
        parejas_asistencias = []
        for i, jug1 in enumerate(jugadores):
            for j, jug2 in enumerate(jugadores):
                if i < j:  # Evitar duplicados
                    asistencias_totales = matriz_asistencias.loc[jug1, jug2] + matriz_asistencias.loc[jug2, jug1]
                    parejas_asistencias.append({
                        'pareja': f"{jug1} ↔ {jug2}",
                        'asistencias_totales': asistencias_totales
                    })
        
        df_parejas = pd.DataFrame(parejas_asistencias)
        df_parejas = df_parejas.sort_values('asistencias_totales', ascending=False).head(10)
        
        if not df_parejas.empty:
            fig_parejas = px.bar(
                df_parejas,
                x='pareja',
                y='asistencias_totales',
                title="Top 10 Parejas - Asistencias Totales",
                labels={'asistencias_totales': 'Asistencias Totales', 'pareja': 'Pareja'}
            )
            fig_parejas.update_xaxis(tickangle=45)
            st.plotly_chart(fig_parejas, use_container_width=True)
    
    @staticmethod
    def _render_rebotes_analysis(df):
        """Renderiza análisis de rebotes entre jugadores"""
        st.subheader("🏀 Análisis de Rebotes")
        
        jugadores = df['nombre_jugador'].unique()
        
        # Análisis de rebotes ofensivos vs defensivos
        rebotes_analysis = []
        
        for jugador in jugadores:
            df_jugador = df[df['nombre_jugador'] == jugador]
            if not df_jugador.empty:
                rebotes_analysis.append({
                    'jugador': jugador,
                    'rebotes_of': df_jugador['rebotes_of'].mean(),
                    'rebotes_def': df_jugador['rebotes_def'].mean(),
                    'rebotes_tot': df_jugador['rebotes_tot'].mean(),
                    'porcentaje_of': (df_jugador['rebotes_of'].mean() / df_jugador['rebotes_tot'].mean() * 100) if df_jugador['rebotes_tot'].mean() > 0 else 0
                })
        
        df_rebotes = pd.DataFrame(rebotes_analysis)
        df_rebotes = df_rebotes.sort_values('rebotes_tot', ascending=False)
        
        # Gráfico de comparación de rebotes
        fig_rebotes = px.bar(
            df_rebotes,
            x='jugador',
            y=['rebotes_of', 'rebotes_def', 'rebotes_tot'],
            title="Análisis de Rebotes por Jugador",
            labels={'value': 'Rebotes Promedio', 'variable': 'Tipo'},
            barmode='group'
        )
        st.plotly_chart(fig_rebotes, use_container_width=True)
        
        # Tabla de especialistas en rebotes
        st.subheader("📊 Especialistas en Rebotes")
        
        especialista_of = df_rebotes.loc[df_rebotes['porcentaje_of'].idxmax()]
        especialista_def = df_rebotes.loc[df_rebotes['rebotes_def'].idxmax()]
        especialista_tot = df_rebotes.loc[df_rebotes['rebotes_tot'].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Mejor Rebotador Ofensivo",
                especialista_of['jugador'],
                f"{especialista_of['porcentaje_of']:.1f}%"
            )
        
        with col2:
            st.metric(
                "Mejor Rebotador Defensivo",
                especialista_def['jugador'],
                f"{especialista_def['rebotes_def']:.1f}"
            )
        
        with col3:
            st.metric(
                "Mejor Rebotador Total",
                especialista_tot['jugador'],
                f"{especialista_tot['rebotes_tot']:.1f}"
            )
    
    @staticmethod
    def _render_sinergia_analysis(df):
        """Renderiza análisis de sinergia general"""
        st.subheader("🤝 Análisis de Sinergia General")
        
        # Calcular sinergia basada en estadísticas compartidas
        jugadores = df['nombre_jugador'].unique()
        
        sinergia_matrix = pd.DataFrame(
            index=jugadores,
            columns=jugadores,
            data=0.0
        )
        
        for i, jug1 in enumerate(jugadores):
            for j, jug2 in enumerate(jugadores):
                if i != j:
                    df_jug1 = df[df['nombre_jugador'] == jug1]
                    df_jug2 = df[df['nombre_jugador'] == jug2]
                    
                    if not df_jug1.empty and not df_jug2.empty:
                        # Calcular sinergia basada en múltiples factores
                        sinergia = 0
                        
                        # Factor 1: Compatibilidad de minutos
                        min_compat = 1 - abs(df_jug1['minutos'].mean() - df_jug2['minutos'].mean()) / 40
                        sinergia += min_compat * 0.3
                        
                        # Factor 2: Compatibilidad de valoración
                        val_compat = 1 - abs(df_jug1['valoracion'].mean() - df_jug2['valoracion'].mean()) / 50
                        sinergia += val_compat * 0.3
                        
                        # Factor 3: Sinergia ofensiva (asistencias + puntos)
                        of_sinergia = (df_jug1['asistencias'].mean() + df_jug2['asistencias'].mean() + 
                                      df_jug1['puntos'].mean() + df_jug2['puntos'].mean()) / 100
                        sinergia += of_sinergia * 0.4
                        
                        sinergia_matrix.loc[jug1, jug2] = min(sinergia, 1.0)
        
        # Visualizar matriz de sinergia
        fig_sinergia = ChartGenerator.create_heatmap(
            sinergia_matrix,
            'columns',
            'index',
            'value',
            "Matriz de Sinergia entre Jugadores"
        )
        
        if fig_sinergia:
            st.plotly_chart(fig_sinergia, use_container_width=True)
        
        # Top parejas por sinergia
        st.subheader("🌟 Mejores Parejas por Sinergia")
        
        parejas_sinergia = []
        for i, jug1 in enumerate(jugadores):
            for j, jug2 in enumerate(jugadores):
                if i < j:
                    sinergia_total = sinergia_matrix.loc[jug1, jug2] + sinergia_matrix.loc[jug2, jug1]
                    parejas_sinergia.append({
                        'pareja': f"{jug1} ↔ {jug2}",
                        'sinergia': sinergia_total
                    })
        
        df_parejas = pd.DataFrame(parejas_sinergia)
        df_parejas = df_parejas.sort_values('sinergia', ascending=False).head(10)
        
        if not df_parejas.empty:
            fig_parejas = px.bar(
                df_parejas,
                x='pareja',
                y='sinergia',
                title="Top 10 Parejas - Sinergia Combinada",
                labels={'sinergia': 'Sinergia', 'pareja': 'Pareja'}
            )
            fig_parejas.update_xaxis(tickangle=45)
            st.plotly_chart(fig_parejas, use_container_width=True)
    
    @staticmethod
    def _render_impacto_analysis(df):
        """Renderiza análisis de impacto en victorias"""
        st.subheader("🏆 Análisis de Impacto en Victorias")
        
        # Calcular impacto de cada jugador y de las parejas
        jugadores = df['nombre_jugador'].unique()
        
        impacto_individual = {}
        for jugador in jugadores:
            df_jugador = df[df['nombre_jugador'] == jugador]
            if not df_jugador.empty:
                # Impacto basado en plus/minus y valoración
                plus_minus = df_jugador['plus_minus'].mean() if 'plus_minus' in df_jugador.columns else 0
                valoracion = df_jugador['valoracion'].mean()
                
                impacto = (plus_minus * 0.6 + valoracion * 0.4)
                impacto_individual[jugador] = impacto
        
        # Calcular impacto de parejas
        parejas_impacto = []
        for i, jug1 in enumerate(jugadores):
            for j, jug2 in enumerate(jugadores):
                if i < j:
                    impacto_pareja = impacto_individual[jug1] + impacto_individual[jug2]
                    parejas_impacto.append({
                        'pareja': f"{jug1} ↔ {jug2}",
                        'impacto': impacto_pareja,
                        'impacto_jug1': impacto_individual[jug1],
                        'impacto_jug2': impacto_individual[jug2]
                    })
        
        df_parejas = pd.DataFrame(parejas_impacto)
        df_parejas = df_parejas.sort_values('impacto', ascending=False).head(15)
        
        # Gráfico de impacto de parejas
        fig_impacto = px.bar(
            df_parejas,
            x='pareja',
            y='impacto',
            title="Top 15 Parejas - Impacto en Victorias",
            labels={'impacto': 'Impacto Combinado', 'pareja': 'Pareja'}
        )
        fig_impacto.update_xaxis(tickangle=45)
        st.plotly_chart(fig_impacto, use_container_width=True)
        
        # Análisis detallado
        st.subheader("📊 Análisis Detallado de Impacto")
        
        # Tabla de impacto individual
        df_impacto_individual = pd.DataFrame([
            {'jugador': jug, 'impacto': imp} 
            for jug, imp in impacto_individual.items()
        ]).sort_values('impacto', ascending=False)
        
        st.write("**Impacto Individual de Jugadores**")
        st.dataframe(df_impacto_individual, use_container_width=True)
        
        # Análisis de qué parejas ayudan más a ganar
        st.subheader("🎯 Parejas que Más Ayudan a Ganar")
        
        # Simular victorias basadas en impacto
        df_parejas['probabilidad_victoria'] = (
            df_parejas['impacto'] / df_parejas['impacto'].max() * 100
        )
        
        df_mejores_parejas = df_parejas.sort_values('probabilidad_victoria', ascending=False).head(5)
        
        if not df_mejores_parejas.empty:
            for _, row in df_mejores_parejas.iterrows():
                st.write(f"**{row['pareja']}**: {row['probabilidad_victoria']:.1f}% probabilidad de victoria")
