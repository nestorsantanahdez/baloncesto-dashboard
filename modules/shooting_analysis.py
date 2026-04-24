import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class ShootingAnalysisModule:
    """Módulo de análisis de tiros avanzado"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de análisis de tiros"""
        st.header("🎯 Análisis de Tiros Avanzado")
        
        # Filtros principales
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            equipos = db_manager.get_equipos()
            equipos.insert(0, "Todos")
            equipo_seleccionado = st.selectbox("Seleccionar Equipo", equipos)
        
        with col2:
            jugadores = db_manager.get_jugadores()
            jugadores.insert(0, "Todos")
            jugador_seleccionado = st.selectbox("Seleccionar Jugador", jugadores)
        
        with col3:
            tipo_tiro = st.selectbox(
                "Tipo de Tiro",
                ["Todos", "T2", "T3", "TL"]
            )
        
        # Filtros adicionales
        with st.expander("🎛️ Filtros Avanzados"):
            col1, col2 = st.columns(2)
            
            with col1:
                zona_cancha = st.selectbox(
                    "Zona de Cancha",
                    ["Todas", "Pintura", "Zona Restringida", "Triple", "Bajo Aro"]
                )
                
                periodo_partido = st.selectbox(
                    "Período del Partido",
                    ["Todos", "1er Cuarto", "2do Cuarto", "3er Cuarto", "4to Cuarto"]
                )
            
            with col2:
                resultado_tiro = st.selectbox(
                    "Resultado del Tiro",
                    ["Todos", "Anotados", "Fallados"]
                )
                
                min_distancia = st.slider(
                    "Distancia Mínima (cm)",
                    min_value=0, max_value=1000, value=0
                )
        
        # Obtener datos
        df_tiros = db_manager.get_tiros(equipo_seleccionado, jugador_seleccionado)
        
        if df_tiros.empty:
            st.warning("No hay datos de tiros disponibles para los filtros seleccionados")
            return
        
        # Aplicar filtros adicionales
        df_filtrado = df_tiros.copy()
        
        # Filtro por tipo de tiro
        if tipo_tiro != "Todos":
            # Necesitaríamos columna de tipo de tiro
            # Por ahora, simulamos basado en distancia
            if tipo_tiro == "T2":
                df_filtrado = df_filtrado[df_filtrado['distancia'] <= 650]
            elif tipo_tiro == "T3":
                df_filtrado = df_filtrado[df_filtrado['distancia'] > 650]
            elif tipo_tiro == "TL":
                # TL sería cerca del aro
                df_filtrado = df_filtrado[df_filtrado['distancia'] <= 450]
        
        # Filtro por zona de cancha
        if zona_cancha != "Todas":
            if zona_cancha == "Pintura":
                df_filtrado = df_filtrado[
                    (df_filtrado['x'] >= 200) & (df_filtrado['x'] <= 800)
                ]
            elif zona_cancha == "Zona Restringida":
                df_filtrado = df_filtrado[
                    (df_filtrado['x'] < 200) | (df_filtrado['x'] > 800)
                ]
            elif zona_cancha == "Triple":
                df_filtrado = df_filtrado[df_filtrado['x'] > 650]
            elif zona_cancha == "Bajo Aro":
                df_filtrado = df_filtrado[
                    (df_filtrado['y'] <= 200) & (df_filtrado['distancia'] <= 300)
                ]
        
        # Filtro por resultado
        if resultado_tiro != "Todos":
            if resultado_tiro == "Anotados":
                df_filtrado = df_filtrado[df_filtrado['anotado'] == True]
            elif resultado_tiro == "Fallados":
                df_filtrado = df_filtrado[df_filtrado['anotado'] == False]
        
        # Filtro por distancia
        if 'distancia' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['distancia'] >= min_distancia]
        
        if df_filtrado.empty:
            st.warning("No hay tiros que cumplan con todos los filtros")
            return
        
        # Renderizar análisis
        ShootingAnalysisModule._render_shot_chart(df_filtrado)
        ShootingAnalysisModule._render_shooting_zones(df_filtrado)
        ShootingAnalysisModule._render_shooting_percentages(df_filtrado)
        ShootingAnalysisModule._render_heatmap_analysis(df_filtrado)
        ShootingAnalysisModule._render_distance_analysis(df_filtrado)
    
    @staticmethod
    def _render_shot_chart(df):
        """Renderiza mapa de tiros en la cancha"""
        st.subheader("🏀 Mapa de Tiros en Cancha")
        
        # Crear shot chart mejorado
        fig = go.Figure()
        
        # Tiros anotados
        tiros_anotados = df[df['anotado'] == True]
        if not tiros_anotados.empty:
            fig.add_trace(go.Scatter(
                x=tiros_anotados['x'],
                y=tiros_anotados['y'],
                mode='markers',
                name='Anotados',
                marker=dict(
                    color='green',
                    size=10,
                    symbol='circle',
                    line=dict(width=1, color='darkgreen'),
                    opacity=0.8
                ),
                text=tiros_anotados.apply(
                    lambda row: f"Dist: {row.get('distancia', 'N/A')}cm", axis=1
                ),
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))
        
        # Tiros fallados
        tiros_fallados = df[df['anotado'] == False]
        if not tiros_fallados.empty:
            fig.add_trace(go.Scatter(
                x=tiros_fallados['x'],
                y=tiros_fallados['y'],
                mode='markers',
                name='Fallados',
                marker=dict(
                    color='red',
                    size=8,
                    symbol='x',
                    line=dict(width=1, color='darkred'),
                    opacity=0.6
                ),
                text=tiros_fallados.apply(
                    lambda row: f"Dist: {row.get('distancia', 'N/A')}cm", axis=1
                ),
                hovertemplate='<b>%{text}</b><extra></extra>'
            ))
        
        # Dibujar cancha de baloncesto
        # Líneas de la cancha
        fig.add_shape(type="rect", x0=0, y0=0, x1=1000, y1=500,
                     line=dict(color="black", width=3), fillcolor="rgba(255,200,100,0.3)")
        
        # Línea de 3 puntos
        fig.add_shape(type="rect", x0=200, y0=0, x1=800, y1=500,
                     line=dict(color="white", width=2), fillcolor="rgba(200,200,200,0.1)")
        
        # Aro
        fig.add_shape(type="circle", x0=500, y0=150, x1=550, y1=200,
                     line=dict(color="orange", width=3))
        
        # Tablero
        fig.add_shape(type="rect", x0=475, y0=50, x1=575, y1=150,
                     line=dict(color="white", width=2), fillcolor="rgba(255,255,255,0.8)")
        
        fig.update_layout(
            title="Mapa de Tiros - Vista Superior",
            xaxis=dict(title="Posición X (cm)", range=[-50, 1050], showgrid=False),
            yaxis=dict(title="Posición Y (cm)", range=[-50, 550], showgrid=False),
            height=600,
            showlegend=True,
            plot_bgcolor='rgba(139,195,74,0.8)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas del shot chart
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Tiros",
                len(df),
                delta=f"{len(df) - len(df[df['anotado'] == True]):+d}"
            )
        
        with col2:
            tiros_anotados_count = len(df[df['anotado'] == True])
            total_tiros = len(df)
            porcentaje = (tiros_anotados_count / total_tiros * 100) if total_tiros > 0 else 0
            st.metric("Tiros Anotados", tiros_anotados_count, f"{porcentaje:.1f}%")
        
        with col3:
            tiros_cerca = len(df[df.get('distancia', 0) <= 450])
            st.metric("Tiros Cerca", tiros_cerca)
        
        with col4:
            tiros_lejos = len(df[df.get('distancia', 0) > 650])
            st.metric("Tiros Lejos", tiros_lejos)
    
    @staticmethod
    def _render_shooting_zones(df):
        """Renderiza análisis por zonas de la cancha"""
        st.subheader("🎯 Análisis por Zonas")
        
        # Definir zonas
        def clasificar_zona(row):
            x, y = row.get('x', 0), row.get('y', 0)
            
            if x < 200 or x > 800:
                return "Fuera de Cancha"
            elif x < 500:
                return "Lado Izquierdo"
            else:
                return "Lado Derecho"
        
        if not df.empty:
            df['zona'] = df.apply(clasificar_zona, axis=1)
            df['distancia_calculada'] = df.apply(
                lambda row: ((row.get('x', 500) - 500)**2 + (row.get('y', 250) - 150)**2)**0.5,
                axis=1
            )
        
        # Estadísticas por zona
        zonas_stats = []
        
        for zona in df['zona'].unique():
            if pd.notna(zona):
                df_zona = df[df['zona'] == zona]
                
                tiros_totales = len(df_zona)
                tiros_anotados = len(df_zona[df_zona['anotado'] == True])
                porcentaje = (tiros_anotados / tiros_totales * 100) if tiros_totales > 0 else 0
                distancia_promedio = df_zona['distancia_calculada'].mean() if 'distancia_calculada' in df_zona.columns else 0
                
                zonas_stats.append({
                    'zona': zona,
                    'tiros_totales': tiros_totales,
                    'tiros_anotados': tiros_anotados,
                    'porcentaje': porcentaje,
                    'distancia_promedio': distancia_promedio
                })
        
        if zonas_stats:
            df_zonas = pd.DataFrame(zonas_stats)
            
            # Gráfico de barras por zona
            fig_zonas = px.bar(
                df_zonas,
                x='zona',
                y='porcentaje',
                title="Porcentaje de Tiro por Zona",
                labels={'porcentaje': 'Porcentaje (%)', 'zona': 'Zona'},
                color='zona',
                text=df_zonas['porcentaje'].round(1)
            )
            
            fig_zonas.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_zonas.update_xaxis(tickangle=45)
            
            st.plotly_chart(fig_zonas, use_container_width=True)
            
            # Tabla detallada
            st.write("**Estadísticas por Zona**")
            df_display = df_zonas[['zona', 'tiros_totales', 'tiros_anotados', 'porcentaje', 'distancia_promedio']]
            df_display.columns = ['Zona', 'Total Tiros', 'Anotados', '% Acierto', 'Distancia Promedio (cm)']
            st.dataframe(df_display, use_container_width=True)
    
    @staticmethod
    def _render_shooting_percentages(df):
        """Renderiza porcentajes de tiro"""
        st.subheader("📊 Porcentajes de Tiro")
        
        # Calcular porcentajes por distancia
        if not df.empty and 'distancia_calculada' not in df.columns:
            df['distancia_calculada'] = df.apply(
                lambda row: ((row.get('x', 500) - 500)**2 + (row.get('y', 250) - 150)**2)**0.5,
                axis=1
            )
        
        # Clasificar tiros por distancia
        def clasificar_distancia(dist):
            if dist <= 300:
                return "Muy Cerca"
            elif dist <= 600:
                return "Cerca"
            elif dist <= 900:
                return "Medio"
            else:
                return "Lejos"
        
        df['rango_distancia'] = df['distancia_calculada'].apply(clasificar_distancia)
        
        # Calcular porcentajes
        porcentajes = []
        
        for rango in df['rango_distancia'].unique():
            if pd.notna(rango):
                df_rango = df[df['rango_distancia'] == rango]
                
                tiros_totales = len(df_rango)
                tiros_anotados = len(df_rango[df_rango['anotado'] == True])
                porcentaje = (tiros_anotados / tiros_totales * 100) if tiros_totales > 0 else 0
                
                porcentajes.append({
                    'rango': rango,
                    'tiros_totales': tiros_totales,
                    'tiros_anotados': tiros_anotados,
                    'porcentaje': porcentaje
                })
        
        if porcentajes:
            df_porcentajes = pd.DataFrame(porcentajes)
            
            # Gráfico de porcentajes
            fig_porcentajes = px.bar(
                df_porcentajes,
                x='rango',
                y='porcentaje',
                title="Porcentaje de Acierto por Distancia",
                labels={'porcentaje': 'Porcentaje (%)', 'rango': 'Rango de Distancia'},
                color='rango',
                text=df_porcentajes['porcentaje'].round(1)
            )
            
            fig_porcentajes.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig_porcentajes, use_container_width=True)
            
            # Tabla de porcentajes
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Porcentaje por Distancia**")
                df_display = df_porcentajes[['rango', 'tiros_totales', 'tiros_anotados', 'porcentaje']]
                df_display.columns = ['Rango', 'Total', 'Anotados', '% Acierto']
                st.dataframe(df_display, use_container_width=True)
            
            with col2:
                # Análisis de tendencias
                st.write("**Tendencias de Tiro**")
                
                total_tiros = len(df)
                tiros_cerca = len(df[df['rango_distancia'].isin(['Muy Cerca', 'Cerca'])])
                tiros_lejos = len(df[df['rango_distancia'].isin(['Medio', 'Lejos'])])
                
                tendencia_cerca = (tiros_cerca / total_tiros * 100) if total_tiros > 0 else 0
                tendencia_lejos = (tiros_lejos / total_tiros * 100) if total_tiros > 0 else 0
                
                st.metric("Tiro Cerca", f"{tendencia_cerca:.1f}%")
                st.metric("Tiro Lejos", f"{tendencia_lejos:.1f}%")
    
    @staticmethod
    def _render_heatmap_analysis(df):
        """Renderiza mapa de calor de tiros"""
        st.subheader("🔥 Mapa de Calor de Tiros")
        
        if df.empty:
            return
        
        # Crear mapa de calor
        fig_heatmap = go.Figure()
        
        # Crear grid para heatmap
        x_bins = range(0, 1100, 100)
        y_bins = range(0, 600, 50)
        
        heatmap_data = []
        
        for i in range(len(x_bins)-1):
            for j in range(len(y_bins)-1):
                x_min, x_max = x_bins[i], x_bins[i+1]
                y_min, y_max = y_bins[j], y_bins[j+1]
                
                # Contar tiros en esta celda
                tiros_celda = df[
                    (df['x'] >= x_min) & (df['x'] < x_max) &
                    (df['y'] >= y_min) & (df['y'] < y_max)
                ]
                
                total_tiros = len(tiros_celda)
                tiros_anotados = len(tiros_celda[tiros_celda['anotado'] == True])
                porcentaje = (tiros_anotados / total_tiros * 100) if total_tiros > 0 else 0
                
                heatmap_data.append([x_min + 50, y_min + 25, porcentaje])
        
        # Crear heatmap
        if heatmap_data:
            x_coords = [point[0] for point in heatmap_data]
            y_coords = [point[1] for point in heatmap_data]
            z_values = [point[2] for point in heatmap_data]
            
            fig_heatmap.add_trace(go.Heatmap(
                x=x_coords,
                y=y_coords,
                z=z_values,
                colorscale='RdYlGn',
                showscale=True,
                hovertemplate='Porcentaje: %{z:.1f}%<extra></extra>'
            ))
        
        fig_heatmap.update_layout(
            title="Mapa de Calor - Porcentaje de Acierto por Zona",
            xaxis=dict(title="Posición X (cm)", range=[0, 1000]),
            yaxis=dict(title="Posición Y (cm)", range=[0, 500]),
            height=500
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    @staticmethod
    def _render_distance_analysis(df):
        """Renderiza análisis por distancia"""
        st.subheader("📏 Análisis por Distancia")
        
        if df.empty or 'distancia_calculada' not in df.columns:
            return
        
        # Gráfico de dispersión distancia vs precisión
        df_distancia = df.copy()
        df_distancia['precision'] = df_distancia['anotado'].astype(int)
        
        fig_distancia = px.scatter(
            df_distancia,
            x='distancia_calculada',
            y='precision',
            color='anotado',
            title="Precisión vs Distancia del Tiro",
            labels={
                'distancia_calculada': 'Distancia (cm)',
                'precision': 'Anotado (1) / Fallado (0)',
                'anotado': 'Resultado'
            },
            color_discrete_map={1: 'Anotado', 0: 'Fallado'}
        )
        
        # Añadir línea de tendencia
        if len(df_distancia) > 10:
            # Calcular precisión promedio por rangos de distancia
            df_tendencia = df_distancia.copy()
            df_tendencia['distancia_rango'] = pd.cut(
                df_tendencia['distancia_calculada'], 
                bins=5, 
                labels=['Muy Cerca', 'Cerca', 'Medio', 'Lejos', 'Muy Lejos']
            )
            
            tendencia = df_tendencia.groupby('distancia_rango')['precision'].mean()
            
            fig_distancia.add_trace(go.Scatter(
                x=[df_distancia['distancia_calculada'].min() + i * (df_distancia['distancia_calculada'].max() - df_distancia['distancia_calculada'].min()) / 4 for i in range(5)],
                y=[tendencia.iloc[i] if i < len(tendencia) else 0 for i in range(5)],
                mode='lines',
                name='Tendencia de Precisión',
                line=dict(color='red', dash='dash')
            ))
        
        st.plotly_chart(fig_distancia, use_container_width=True)
        
        # Estadísticas por rangos de distancia
        st.write("**Estadísticas por Rangos de Distancia**")
        
        df_distancia['rango'] = pd.cut(
            df_distancia['distancia_calculada'],
            bins=[0, 300, 600, 900, 1200],
            labels=['Muy Cerca', 'Cerca', 'Medio', 'Lejos', 'Muy Lejos']
        )
        
        rango_stats = df_distancia.groupby('rango').agg({
            'precision': ['mean', 'count'],
            'distancia_calculada': 'mean'
        }).round(2)
        
        rango_stats.columns = [
            'Precisión Promedio', 'Total Tiros', 'Distancia Promedio'
        ]
        
        st.dataframe(rango_stats, use_container_width=True)
