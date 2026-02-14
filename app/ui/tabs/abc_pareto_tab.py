import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any


class ABCTab:
    """Вкладка с ABC/XYZ анализом и правилом Парето."""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("📊 ABC/XYZ анализ & Правило Парето")

        tab1, tab2, tab3 = st.tabs([
            "📊 ABC-анализ",
            "📈 XYZ-анализ",
            "📉 Правило Парето"
        ])

        with tab1:
            self._render_abc_analysis(df, metrics)
        with tab2:
            self._render_xyz_analysis(df)
        with tab3:
            self._render_pareto_analysis(metrics)

    def _render_abc_analysis(self, df: pd.DataFrame, metrics: Dict[str, Any]):
        st.subheader("ABC Классификация")

        abc_data = metrics.get('abc_xyz', pd.DataFrame())
        if abc_data.empty:
            st.warning("Нет данных для ABC-анализа")
            return

        # Настройки классификации
        col1, col2, _ = st.columns(3)
        with col1:
            a_threshold = st.slider("Порог для класса A (%)", 70, 90, 80, 1)
        with col2:
            b_threshold = st.slider("Порог для класса B (%)", 85, 98, 95, 1)

        # Пересчёт классификации
        abc_data = abc_data.sort_values('value', ascending=False)
        abc_data['cumulative_percentage'] = (
            abc_data['value'].cumsum() / abc_data['value'].sum() * 100
        )

        def assign_class(row):
            if row['cumulative_percentage'] <= a_threshold:
                return 'A'
            elif row['cumulative_percentage'] <= b_threshold:
                return 'B'
            return 'C'

        abc_data['abc_class'] = abc_data.apply(assign_class, axis=1)

        # Визуализация
        fig = go.Figure()

        colors = {'A': 'red', 'B': 'orange', 'C': 'green'}

        for cls in ['A', 'B', 'C']:
            cls_data = abc_data[abc_data['abc_class'] == cls]
            fig.add_trace(go.Bar(
                x=cls_data.get('category', cls_data.get('entity', cls_data.index)),
                y=cls_data['value'],
                name=f'Класс {cls}',
                marker_color=colors[cls],
                text=cls_data['abc_class'],
                textposition='auto'
            ))

        fig.update_layout(
            title='ABC Анализ: Распределение',
            xaxis_title='Категория / Объект',
            yaxis_title='Значение',
            barmode='stack',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Статистика по классам
        st.subheader("Статистика по классам ABC")

        first_col = abc_data.columns[0]  # обычно category или entity
        summary = abc_data.groupby('abc_class').agg({
            first_col: 'count',
            'value': ['sum', 'mean']
        }).round(0)

        summary.columns = ['Количество', 'Сумма', 'Среднее']
        st.dataframe(summary, use_container_width=True)

    def _render_xyz_analysis(self, df: pd.DataFrame):
        st.subheader("XYZ Анализ стабильности")

        if 'date' not in df.columns or 'category' not in df.columns:
            st.warning("Для XYZ анализа нужны колонки 'date' и 'category'")
            return

        st.info("Простая демонстрация XYZ-анализа (в продакшене — реальные расчёты)")

        categories = ['Электроника', 'Одежда', 'Продукты', 'Бытовая техника', 'Косметика']
        stability = ['Высокая', 'Средняя', 'Низкая', 'Средняя', 'Высокая']
        cv = [8.2, 15.5, 30.1, 18.3, 9.7]

        xyz_data = pd.DataFrame({
            'category': categories,
            'стабильность': stability,
            'коэффициент_вариации': cv
        })

        fig = px.bar(
            xyz_data,
            x='category',
            y='коэффициент_вариации',
            color='стабильность',
            title='Коэффициент вариации по категориям',
            labels={'коэффициент_вариации': 'Коэффициент вариации, %'}
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_pareto_analysis(self, metrics: Dict[str, Any]):
        st.subheader("Правило Парето (80/20)")

        pareto_data = metrics.get('pareto_entity', pd.DataFrame())
        if pareto_data.empty:
            st.warning("Нет данных для Парето-анализа")
            return

        pareto_data = pareto_data.sort_values('value', ascending=False)
        pareto_data['cumulative_percentage'] = (
            pareto_data['value'].cumsum() / pareto_data['value'].sum() * 100
        )
        pareto_data['is_top_80'] = pareto_data['cumulative_percentage'] <= 80

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=pareto_data.get('entity', pareto_data.index),
            y=pareto_data['value'],
            name='Значение',
            marker_color='lightblue'
        ))

        fig.add_trace(go.Scatter(
            x=pareto_data.get('entity', pareto_data.index),
            y=pareto_data['cumulative_percentage'],
            name='Кумулятивный %',
            yaxis='y2',
            line=dict(color='red', width=3)
        ))

        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="80%")

        fig.update_layout(
            title='Кривая Парето',
            xaxis_title='Объект',
            yaxis_title='Значение',
            yaxis2=dict(title='Кумулятивный %', overlaying='y', side='right', range=[0, 100]),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        top_80 = pareto_data[pareto_data['is_top_80']]
        st.info(f"**{len(top_80)} из {len(pareto_data)}** объектов дают **80%** всего значения")