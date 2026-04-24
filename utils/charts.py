import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class ChartGenerator:
    """Generador de gráficos personalizados para el dashboard de baloncesto"""
    
    @staticmethod
    def create_radar_chart(df, columns, title, color_scheme='viridis'):
        """Crea un gráfico de radar (telaraña)"""
        if df.empty or len(columns) == 0:
            return None
            
        fig = go.Figure()
        
        for idx, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[col] for col in columns],
                theta=columns,
                fill='toself',
                name=row.get('nombre_jugador', f'Jugador {idx+1}'),
                line_color=px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([row[col].max() for col in columns]) * 1.1]
                )
            ),
            title=title,
            showlegend=True,
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_comparison_bar_chart(df, metric_columns, title, group_col='nombre_jugador'):
        """Crea gráfico de barras comparativo"""
        if df.empty or len(metric_columns) == 0:
            return None
            
        # Preparar datos para el gráfico
        df_melted = df.melt(
            id_vars=[group_col],
            value_vars=metric_columns,
            var_name='Métrica',
            value_name='Valor'
        )
        
        fig = px.bar(
            df_melted,
            x=group_col,
            y='Valor',
            color='Métrica',
            title=title,
            barmode='group',
            height=500
        )
        
        fig.update_layout(
            xaxis_title=group_col.replace('_', ' ').title(),
            yaxis_title='Valor',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_shot_chart(df_tiros, title="Mapa de Tiros"):
        """Crea un mapa de tiros en la cancha"""
        if df_tiros.empty:
            return None
            
        fig = go.Figure()
        
        # Tiros anotados
        tiros_anotados = df_tiros[df_tiros['anotado'] == True]
        if not tiros_anotados.empty:
            fig.add_trace(go.Scatter(
                x=tiros_anotados['x'],
                y=tiros_anotados['y'],
                mode='markers',
                name='Anotados',
                marker=dict(
                    color='green',
                    size=8,
                    symbol='circle',
                    line=dict(width=1, color='darkgreen')
                )
            ))
        
        # Tiros fallados
        tiros_fallados = df_tiros[df_tiros['anotado'] == False]
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
                    line=dict(width=1, color='darkred')
                )
            ))
        
        # Dibujar cancha
        fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=50,
                     line=dict(color="black", width=2), fillcolor="rgba(255,255,255,0)")
        
        fig.update_layout(
            title=title,
            xaxis=dict(title="Posición X (cm)", range=[-10, 110]),
            yaxis=dict(title="Posición Y (cm)", range=[-10, 60]),
            height=600,
            showlegend=True,
            plot_bgcolor='white'
        )
        
        return fig
    
    @staticmethod
    def create_gantt_chart(df, title="Distribución de Minutos por Partido"):
        """Crea un diagrama de Gantt para minutos por partido"""
        if df.empty:
            return None
            
        # Preparar datos para Gantt
        df_gantt = df.copy()
        df_gantt['start'] = 0
        df_gantt['finish'] = df_gantt['minutos']
        
        fig = px.timeline(
            df_gantt,
            x_start="start",
            x_end="finish",
            y="nombre_jugador",
            color="equipo_nombre",
            title=title,
            height=400
        )
        
        fig.update_layout(
            xaxis_title="Minutos Jugados",
            yaxis_title="Jugador",
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(df, x_col, y_col, value_col, title="Mapa de Calor"):
        """Crea un mapa de calor"""
        if df.empty:
            return None
            
        # Pivot table para heatmap
        pivot_table = df.pivot_table(
            values=value_col,
            index=y_col,
            columns=x_col,
            aggfunc='mean',
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_table,
            title=title,
            labels=dict(x=x_col.replace('_', ' ').title(), 
                      y=y_col.replace('_', ' ').title(), 
                      color=value_col.replace('_', ' ').title()),
            color_continuous_scale='viridis'
        )
        
        return fig
    
    @staticmethod
    def create_trend_line(df, x_col, y_col, title="Tendencia Temporal"):
        """Crea gráfico de línea con tendencia"""
        if df.empty:
            return None
            
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            markers=True
        )
        
        # Añadir línea de tendencia
        if len(df) > 1:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col].rolling(window=3).mean(),
                mode='lines',
                name='Tendencia',
                line=dict(color='red', dash='dash')
            ))
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_box_plot(df, metric_col, group_col, title="Distribución"):
        """Crea gráfico de caja (box plot)"""
        if df.empty:
            return None
            
        fig = px.box(
            df,
            x=group_col,
            y=metric_col,
            title=title,
            height=400
        )
        
        fig.update_layout(
            xaxis_title=group_col.replace('_', ' ').title(),
            yaxis_title=metric_col.replace('_', ' ').title()
        )
        
        return fig
    
    @staticmethod
    def create_pie_chart(df, value_col, title="Distribución"):
        """Crea gráfico circular"""
        if df.empty:
            return None
            
        fig = px.pie(
            df,
            values=value_col,
            names=df.index if hasattr(df.index, 'name') else range(len(df)),
            title=title,
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_scatter_plot(df, x_col, y_col, color_col=None, title="Gráfico de Dispersión"):
        """Crea gráfico de dispersión"""
        if df.empty:
            return None
            
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            height=500
        )
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
