import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

class ChartsTab:
    """Вкладка с графиками и трендами — универсальная"""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("📈 Расширенная аналитика: графики и тренды")

        self._render_time_series(df)
        self._render_comparative_analysis(df)
        self._render_heatmap(df)

    def _render_time_series(self, df: pd.DataFrame):
        if 'date' not in df.columns or df.empty:
            return

        st.subheader("📅 Динамика во времени")

        freq = st.radio("Частота агрегации", ["Дни", "Недели", "Месяцы"], horizontal=True)

        if freq == "Дни":
            period_df = df.groupby('date')['value'].sum().reset_index()
        elif freq == "Недели":
            df['week'] = df['date'].dt.to_period('W').dt.start_time
            period_df = df.groupby('week')['value'].sum().reset_index().rename(columns={'week': 'date'})
        else:
            df['month'] = df['date'].dt.to_period('M').dt.start_time
            period_df = df.groupby('month')['value'].sum().reset_index().rename(columns={'month': 'date'})

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=period_df['date'], y=period_df['value'],
                                 mode='lines+markers', name='Фактические значения',
                                 line=dict(color='#EF4444', width=3)))

        if len(period_df) > 7:
            period_df['ma_7'] = period_df['value'].rolling(7, min_periods=1).mean()
            fig.add_trace(go.Scatter(x=period_df['date'], y=period_df['ma_7'],
                                     mode='lines', name='Скользящее среднее (7)',
                                     line=dict(color='#3B82F6', width=3, dash='dash')))

        fig.update_layout(
            title=f"Динамика ({freq.lower()})",
            xaxis_title="Дата",
            yaxis_title="Значение, ₽",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_comparative_analysis(self, df: pd.DataFrame):
        st.subheader("🔄 Сравнительный анализ")
        col1, col2 = st.columns(2)

        with col1:
            if 'date' in df.columns:
                df['day_of_week'] = df['date'].dt.day_name()
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_loss = df.groupby('day_of_week')['value'].sum().reindex(weekday_order)

                fig = px.bar(x=weekday_loss.index, y=weekday_loss.values,
                             title='По дням недели',
                             labels={'x': 'День недели', 'y': 'Значение, ₽'},
                             color=weekday_loss.values,
                             color_continuous_scale='reds')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'date' in df.columns:
                df['hour'] = df['date'].dt.hour
                hour_loss = df.groupby('hour')['value'].sum()
                fig = px.line(x=hour_loss.index, y=hour_loss.values,
                              title='По часам',
                              labels={'x': 'Час', 'y': 'Значение, ₽'})
                st.plotly_chart(fig, use_container_width=True)

    def _render_heatmap(self, df: pd.DataFrame):
        if 'date' not in df.columns:
            return

        st.subheader("🌡️ Heatmap интенсивности")

        try:
            df['day_of_week_num'] = df['date'].dt.dayofweek
            df['hour'] = df['date'].dt.hour

            heatmap_data = df.groupby(['day_of_week_num', 'hour'])['value'].sum().unstack(fill_value=0)
            heatmap_data = heatmap_data.reindex(columns=range(24), fill_value=0)
            heatmap_data = heatmap_data.reindex(index=range(7), fill_value=0)

            day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

            fig = px.imshow(heatmap_data.values,
                            title='Интенсивность: День недели × Час',
                            labels=dict(x="Час", y="День недели", color="Значение"),
                            x=list(range(24)),
                            y=day_names,
                            color_continuous_scale='reds',
                            aspect='auto')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Не удалось построить heatmap: {str(e)[:80]}")