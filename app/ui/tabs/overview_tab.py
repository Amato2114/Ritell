import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

class OverviewTab:
    """Главная вкладка — обзор + ключевые метрики"""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("📊 Обзор потерь / значений")

        # Главная карточка
        total = metrics.get('current_value', 0)
        st.markdown(f"""
        <div style="text-align:center; padding:3rem; background:linear-gradient(135deg,#FF4B4B,#EF4444); 
                    border-radius:20px; color:white; margin-bottom:2rem;">
            <h1 style="font-size:4rem; margin:0;">{total:,.0f} ₽</h1>
            <p style="font-size:1.5rem; margin:0;">Общее значение за период</p>
        </div>
        """, unsafe_allow_html=True)

        # Метрики в колонках
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("A-класс (80%)", f"{metrics.get('a_class_value', 0):,.0f} ₽")
        with col2:
            st.metric("Пиковые дни (20%)", f"{metrics.get('peak_days_value', 0):,.0f} ₽")
        with col3:
            st.metric("Топ-объекты (80%)", f"{metrics.get('top_entity_value', 0):,.0f} ₽")
        with col4:
            st.metric("Годовая экстраполяция", f"{metrics.get('annual_savings', 0):,.0f} ₽")

        # What-if сценарии
        st.subheader("🔮 Потенциальная экономия (What-if)")
        cols = st.columns(5)
        scenarios = metrics.get('scenarios', {})
        with cols[0]: st.metric("A-класс", f"{metrics.get('savings_a', 0):,.0f} ₽", f"-{scenarios.get('reduce_a', 0)}%")
        with cols[1]: st.metric("Пиковые дни", f"{metrics.get('savings_peak', 0):,.0f} ₽", f"-{scenarios.get('reduce_peak', 0)}%")
        with cols[2]: st.metric("Топ-объекты", f"{metrics.get('savings_entity', 0):,.0f} ₽", f"-{scenarios.get('reduce_top_entity', 0)}%")
        with cols[3]: st.metric("Итого за период", f"{metrics.get('total_savings', 0):,.0f} ₽")
        with cols[4]: 
            roi = metrics.get('roi', 0)
            st.metric("ROI", f"{roi:.1f}%", "Эффективность" if roi > 0 else None)

        # Топ-10 объектов и категорий
        colA, colB = st.columns(2)
        with colA:
            st.subheader("🏪 Топ-10 объектов")
            if not metrics.get('entity_losses', pd.DataFrame()).empty:
                st.dataframe(metrics['entity_losses'].head(10), use_container_width=True)
        with colB:
            st.subheader("📦 Топ-10 категорий")
            if not metrics.get('category_losses', pd.DataFrame()).empty:
                st.dataframe(metrics['category_losses'].head(10), use_container_width=True)