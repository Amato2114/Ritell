import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any

class AnomaliesTab:
    """Вкладка аномалий — универсальная (value вместо loss_amount)"""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("🔍 Детектор аномалий & Кластеризация")

        tab1, tab2 = st.tabs(["📊 Статистические аномалии", "🔬 Кластерный анализ"])

        with tab1:
            self._render_statistical_anomalies(df)
        with tab2:
            self._render_cluster_analysis(df)

    def _render_statistical_anomalies(self, df: pd.DataFrame):
        st.subheader("Методы обнаружения аномалий")

        if df.empty or 'value' not in df.columns:
            st.warning("Недостаточно данных")
            return

        method = st.selectbox("Метод", ["Isolation Forest (имитация)", "Z-Score", "IQR", "Процентный порог"])

        # Подготовка
        values = df['value'].values.reshape(-1, 1)

        if method == "Z-Score":
            threshold = st.slider("Z-Score порог", 2.0, 5.0, 3.0, 0.1)
            z = np.abs((df['value'] - df['value'].mean()) / df['value'].std())
            df['is_anomaly'] = z > threshold
        elif method == "IQR":
            mult = st.slider("IQR множитель", 1.0, 3.0, 1.5, 0.1)
            Q1, Q3 = np.percentile(df['value'], [25, 75])
            IQR = Q3 - Q1
            df['is_anomaly'] = (df['value'] < Q1 - mult * IQR) | (df['value'] > Q3 + mult * IQR)
        else:  # Процентный порог или имитация
            perc = st.slider("Перцентиль", 90, 99, 95, 1)
            thresh = np.percentile(df['value'], perc)
            df['is_anomaly'] = df['value'] > thresh

        anomalies = df[df['is_anomaly']]

        col1, col2, col3 = st.columns(3)
        col1.metric("Всего записей", len(df))
        col2.metric("Аномалий", len(anomalies))
        col3.metric("Доля", f"{len(anomalies)/len(df)*100:.1f}%" if len(df) else "0%")

        # График
        fig = go.Figure()
        normal = df[~df['is_anomaly']]
        fig.add_trace(go.Scatter(x=normal.index, y=normal['value'], mode='markers', name='Нормальные', marker=dict(color='blue', size=6)))
        fig.add_trace(go.Scatter(x=anomalies.index, y=anomalies['value'], mode='markers', name='Аномалии', marker=dict(color='red', size=10, symbol='x')))
        fig.update_layout(title=f"Аномалии ({method})", xaxis_title="Индекс / Дата", yaxis_title="Значение, ₽", height=500)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Детализация аномалий"):
            st.dataframe(anomalies.sort_values('value', ascending=False).head(50), use_container_width=True)

    def _render_cluster_analysis(self, df: pd.DataFrame):
        st.subheader("Кластеризация объектов")
        if 'entity' not in df.columns:
            st.warning("Нужна колонка entity")
            return

        stats = df.groupby('entity')['value'].agg(['sum', 'mean', 'count']).round(0)
        stats.columns = ['Сумма', 'Среднее', 'Количество']
        stats = stats.sort_values('Сумма', ascending=False)
        st.dataframe(stats.head(20), use_container_width=True)