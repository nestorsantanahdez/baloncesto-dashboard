import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.charts import ChartGenerator
from utils.helpers import DataHelpers

class TeamDynamicsModule:
    """Módulo de análisis de dinámica de equipo"""
    
    @staticmethod
    def render(db_manager):
        """Renderiza el módulo de dinámica de equipo"""
        st.header("⚔️ Análisis de Dinámica de Equipo")
        
        # Filtros principales
        col1, col2 = st.columns([2, 1])
        
        with col1:
            equipos = db_manager.get_equipos()
            equipos.insert(0, "Todos")
            equipo_seleccionado = st.selectbox("Seleccionar Equipo", equipos)
        
        with col2:
            tipo_analisis = st.selectbox(
                "Tipo de Análisis",
                ["Distribución de Minutos", "Rendimiento por Victorias/Derrotas", "Análisis de Quintetos", "Consistencia del Equipo"]
            )
        
        # Obtener datos
        df_jugadores = db_manager.get_estadisticas_jugadores(equipo_seleccionado)
        
        if df_jugadores.empty:
            st.warning("No hay datos disponibles para el análisis")
            return
        
        # Renderizar según tipo seleccionado
        if tipo_analisis == "Distribución de Minutos":
            TeamDynamicsModule._render_minutes_distribution(df_jugadores)
        elif tipo_analisis == "Rendimiento por Victorias/Derrotas":
            TeamDynamicsModule._render_win_loss_performance(df_jugadores)
        elif tipo_analisis == "Análisis de Quintetos":
            TeamDynamicsModule._render_lineup_analysis(df_jugadores)
        elif tipo_analisis == "Consistencia del Equipo":
            TeamDynamicsModule._render_consistency_analysis(df_jugadores)
    
    @staticmethod
    def _render_minutes_distribution(df):
        """Renderiza distribución de minutos por partido"""
        st.subheader("⏱️ Distribución de Minutos por Partido")
        
        # Diagrama de Gantt
        fig_gantt = ChartGenerator.create_gantt_chart(
            df,
            "Distribución de Minutos por Partido"
        )
        
        if fig_gantt:
            st.plotly_chart(fig_gantt, use_container_width=True)
        
        # Estadísticas de minutos
        st.subheader("📊 Estadísticas de Minutos")
        
        df_minutos = df.groupby('nombre_jugador').agg({
            'minutos': ['mean', 'sum', 'std'],
            'partidos': 'count'
        }).reset_index()
        
        df_minutos.columns = ['Jugador', 'Minutos Promedio', 'Minutos Totales', 'Desviación', 'Partidos']
        
        # Resaltar jugadores con más minutos
        df_minutos_display = DataHelpers.highlight_best_values(
            df_minutos,
            ['Minutos Promedio', 'Minutos Totales']
        )
        
        st.dataframe(df_minutos_display, use_container_width=True)
        
        # Gráfico de distribución de minutos
        fig_distribucion = px.box(
            df,
            x='nombre_jugador',
            y='minutos',
            title="Distribución de Minutos Jugados",
            labels={'minutos': 'Minutos', 'nombre_jugador': 'Jugador'}
        )
        
        st.plotly_chart(fig_distribucion, use_container_width=True)
        
        # Análisis de carga de trabajo
        st.subheader("🏋️ Análisis de Carga de Trabajo")
        
        # Calcular jugadores sobreutilizados o subutilizados
        minutos_promedio = df['minutos'].mean()
        desviacion_estandar = df['minutos'].std()
        
        df_carga = df.groupby('nombre_jugador')['minutos'].agg(['mean', 'std']).reset_index()
        df_carga['utilizacion'] = df_carga['mean'].apply(
            lambda x: 'Sobreutilizado' if x > minutos_promedio + desviacion_estandar 
            else 'Subutilizado' if x < minutos_promedio - desviacion_estandar 
            else 'Normal'
        )
        
        fig_carga = px.scatter(
            df_carga,
            x='mean',
            y='std',
            color='utilizacion',
            title="Análisis de Carga de Trabajo",
            labels={
                'mean': 'Minutos Promedio',
                'std': 'Variabilidad',
                'utilizacion': 'Utilización'
            },
            color_discrete_map={
                'Sobreutilizado': 'red',
                'Normal': 'green',
                'Subutilizado': 'orange'
            }
        )
        
        st.plotly_chart(fig_carga, use_container_width=True)
    
    @staticmethod
    def _render_win_loss_performance(df):
        """Renderiza rendimiento por victorias/derrotas"""
        st.subheader("🏆 Rendimiento por Victorias/Derrotas")
        
        # Simular resultados basados en plus/minus
        df['resultado'] = df['plus_minus'].apply(lambda x: 'Victoria' if x > 0 else 'Derrota')
        
        # Estadísticas por resultado
        stats_resultado = df.groupby('resultado').agg({
            'puntos': 'mean',
            'rebotes_tot': 'mean',
            'asistencias': 'mean',
            'valoracion': 'mean',
            'minutos': 'mean',
            'partidos': 'count'
        }).reset_index()
        
        # Métricas clave
        col1, col2, col3, col4 = st.columns(4)
        
        if not stats_resultado.empty:
            df_victorias = stats_resultado[stats_resultado['resultado'] == 'Victoria']
            df_derrotas = stats_resultado[stats_resultado['resultado'] == 'Derrota']
            
            with col1:
                if not df_victorias.empty:
                    st.metric(
                        "Puntos en Victorias",
                        f"{df_victorias['puntos'].iloc[0]:.1f}"
                    )
            
            with col2:
                if not df_derrotas.empty:
                    st.metric(
                        "Puntos en Derrotas",
                        f"{df_derrotas['puntos'].iloc[0]:.1f}"
                    )
            
            with col3:
                if not df_victorias.empty:
                    st.metric(
                        "Valoración en Victorias",
                        f"{df_victorias['valoracion'].iloc[0]:.1f}"
                    )
            
            with col4:
                if not df_derrotas.empty:
                    st.metric(
                        "Valoración en Derrotas",
                        f"{df_derrotas['valoracion'].iloc[0]:.1f}"
                    )
        
        # Gráfico comparativo
        fig_comparativo = px.bar(
            stats_resultado,
            x='resultado',
            y=['puntos', 'rebotes_tot', 'asistencias', 'valoracion'],
            title="Rendimiento: Victorias vs Derrotas",
            labels={'value': 'Promedio', 'variable': 'Estadística'},
            barmode='group'
        )
        
        st.plotly_chart(fig_comparativo, use_container_width=True)
        
        # Análisis de jugadores "clutch"
        st.subheader("🎯 Jugadores Clutch (Rendimiento en momentos clave)")
        
        # Identificar jugadores que mejoran en victorias vs derrotas
        df_performance = df.groupby(['nombre_jugador', 'resultado'])['valoracion'].mean().reset_index()
        
        jugadores_clutch = []
        
        for jugador in df['nombre_jugador'].unique():
            df_jugador = df_performance[df_performance['nombre_jugador'] == jugador]
            
            if len(df_jugador) == 2:  # Tiene datos de victoria y derrota
                val_victoria = df_jugador[df_jugador['resultado'] == 'Victoria']['valoracion'].iloc[0]
                val_derrota = df_jugador[df_jugador['resultado'] == 'Derrota']['valoracion'].iloc[0]
                
                mejora_clutch = val_victoria - val_derrota
                jugadores_clutch.append({
                    'jugador': jugador,
                    'mejora_clutch': mejora_clutch,
                    'val_victoria': val_victoria,
                    'val_derrota': val_derrota
                })
        
        if jugadores_clutch:
            df_clutch = pd.DataFrame(jugadores_clutch)
            df_clutch = df_clutch.sort_values('mejora_clutch', ascending=False).head(10)
            
            fig_clutch = px.bar(
                df_clutch,
                x='jugador',
                y='mejora_clutch',
                title="Top 10 Jugadores Clutch (Mejora en Victorias)",
                labels={'mejora_clutch': 'Mejora Valoración', 'jugador': 'Jugador'},
                color='mejora_clutch',
                color_continuous_scale='RdYlGn'
            )
            
            st.plotly_chart(fig_clutch, use_container_width=True)
    
    @staticmethod
    def _render_lineup_analysis(df):
        """Renderiza análisis de quintetos"""
        st.subheader("👥 Análisis de Quintetos")
        
        # Simular quintetos basados en minutos
        # Agrupar por partido y ordenar por minutos
        df_quintetos = df.sort_values(['partido_id', 'minutos'], ascending=[True, False])
        
        quintetos_optimos = []
        
        for partido_id in df_quintetos['partido_id'].unique():
            df_partido = df_quintetos[df_quintetos['partido_id'] == partido_id]
            
            if not df_partido.empty:
                # Tomar top 5 jugadores con más minutos en ese partido
                quinteto = df_partido.nlargest(5, 'minutos')['nombre_jugador'].tolist()
                valoracion_quinteto = df_partido.nlargest(5, 'minutos')['valoracion'].sum()
                
                quintetos_optimos.append({
                    'partido_id': partido_id,
                    'quinteto': quinteto,
                    'valoracion_total': valoracion_quinteto,
                    'minutos_promedio': df_partido.nlargest(5, 'minutos')['minutos'].mean()
                })
        
        if quintetos_optimos:
            df_quintetos = pd.DataFrame(quintetos_optimos)
            
            # Quintetos más utilizados
            st.write("### 🏀 Quintetos Más Frecuentes")
            
            # Contar combinaciones de quintetos
            from collections import Counter
            
            quintetos_str = [' | '.join(sorted(q)) for q in df_quintetos['quinteto'].tolist()]
            contador_quintetos = Counter(quintetos_str)
            
            quintetos_frecuentes = pd.DataFrame([
                {'quinteto': quinteto, 'frecuencia': freq}
                for quinteto, freq in contador_quintetos.most_common(10)
            ])
            
            fig_frecuencia = px.bar(
                quintetos_frecuentes,
                x='frecuencia',
                y='quinteto',
                orientation='h',
                title="Top 10 Quintetos Más Utilizados",
                labels={'frecuencia': 'Frecuencia', 'quinteto': 'Quinteto'}
            )
            
            fig_frecuencia.update_yaxis(tickangle=45)
            st.plotly_chart(fig_frecuencia, use_container_width=True)
            
            # Quintetos más efectivos
            st.write("### 🌟 Quintetos Más Efectivos")
            
            efectividad_quintetos = []
            
            for quinteto_str, freq in contador_quintetos.items():
                if freq >= 2:  # Quintetos usados al menos 2 veces
                    # Calcular efectividad promedio
                    partidos_con_quinteto = df_quintetos[
                        df_quintetos['quinteto'].apply(
                            lambda x: ' | '.join(sorted(x)) == quinteto_str
                        )
                    ]
                    
                    if not partidos_con_quinteto.empty:
                        efectividad_promedio = partidos_con_quinteto['valoracion_total'].mean()
                        
                        efectividad_quintetos.append({
                            'quinteto': quinteto_str,
                            'frecuencia': freq,
                            'efectividad_promedio': efectividad_promedio,
                            'partidos': len(partidos_con_quinteto)
                        })
            
            if efectividad_quintetos:
                df_efectividad = pd.DataFrame(efectividad_quintetos)
                df_efectividad = df_efectividad.sort_values('efectividad_promedio', ascending=False).head(10)
                
                fig_efectividad = px.bar(
                    df_efectividad,
                    x='efectividad_promedio',
                    y='quinteto',
                    orientation='h',
                    title="Top 10 Quintetos Más Efectivos",
                    labels={
                        'efectividad_promedio': 'Valoración Promedio',
                        'quinteto': 'Quinteto'
                    },
                    color='efectividad_promedio',
                    color_continuous_scale='Viridis'
                )
                
                fig_efectividad.update_yaxis(tickangle=45)
                st.plotly_chart(fig_efectividad, use_container_width=True)
                
                # Tabla de quintetos
                df_efectividad_display = df_efectividad.copy()
                df_efectividad_display.columns = [
                    'Quinteto', 'Frecuencia', 'Valoración Promedio', 'Partidos'
                ]
                
                st.dataframe(df_efectividad_display, use_container_width=True)
    
    @staticmethod
    def _render_consistency_analysis(df):
        """Renderiza análisis de consistencia del equipo"""
        st.subheader("📈 Análisis de Consistencia del Equipo")
        
        # Calcular consistencia por partido
        consistencia_partidos = []
        
        for partido_id in df['partido_id'].unique():
            df_partido = df[df['partido_id'] == partido_id]
            
            if not df_partido.empty:
                # Calcular desviación estándar de valoración en el partido
                valoracion_std = df_partido['valoracion'].std()
                valoracion_mean = df_partido['valoracion'].mean()
                
                # Consistencia = 100 - (desviación / media * 100)
                consistencia = max(0, 100 - (valoracion_std / valoracion_mean * 100)) if valoracion_mean > 0 else 0
                
                consistencia_partidos.append({
                    'partido_id': partido_id,
                    'consistencia': consistencia,
                    'valoracion_promedio': valoracion_mean,
                    'valoracion_std': valoracion_std,
                    'jugadores': len(df_partido)
                })
        
        if consistencia_partidos:
            df_consistencia = pd.DataFrame(consistencia_partidos)
            df_consistencia = df_consistencia.sort_values('partido_id')
            
            # Evolución de consistencia
            fig_evolucion = px.line(
                df_consistencia,
                x='partido_id',
                y='consistencia',
                title="Evolución de Consistencia del Equipo",
                labels={
                    'consistencia': 'Consistencia (%)',
                    'partido_id': 'Partido'
                },
                markers=True
            )
            
            # Añadir línea de tendencia
            fig_evolucion.add_trace(go.Scatter(
                x=df_consistencia['partido_id'],
                y=df_consistencia['consistencia'].rolling(window=5).mean(),
                mode='lines',
                name='Tendencia',
                line=dict(color='red', dash='dash')
            ))
            
            st.plotly_chart(fig_evolucion, use_container_width=True)
            
            # Estadísticas de consistencia
            st.write("### 📊 Estadísticas de Consistencia")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Consistencia Promedio",
                    f"{df_consistencia['consistencia'].mean():.1f}%"
                )
            
            with col2:
                st.metric(
                    "Consistencia Máxima",
                    f"{df_consistencia['consistencia'].max():.1f}%"
                )
            
            with col3:
                st.metric(
                    "Consistencia Mínima",
                    f"{df_consistencia['consistencia'].min():.1f}%"
                )
            
            # Análisis de factores de consistencia
            st.subheader("🔍 Factores que Afectan la Consistencia")
            
            # Correlación entre variables
            df_corr = df[['minutos', 'valoracion', 'puntos', 'rebotes_tot', 'asistencias']].corr()
            
            fig_corr = px.imshow(
                df_corr,
                title="Correlación: Factores de Consistencia",
                color_continuous_scale='RdBu',
                labels=dict(x="Variable", y="Variable", color="Correlación")
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Identificar partidos más consistentes
            st.write("### 🌟 Partidos Más Consistentes")
            
            partidos_top = df_consistencia.nlargest(5, 'consistencia')
            
            for _, partido in partidos_top.iterrows():
                st.write(f"**Partido {partido['partido_id']}**: {partido['consistencia']:.1f}% consistencia")
