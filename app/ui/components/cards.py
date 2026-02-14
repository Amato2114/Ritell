# app/ui/components/cards.py
import streamlit as st


class MetricCards:
    """Компоненты метрик и карточек"""
    
    @staticmethod
    def render_main_metrics(metrics: dict):
        """Рендерит главные метрики"""
        current_losses = metrics.get('current_losses', 0)
        
        st.markdown(f"""
        <div style="
            text-align: center; 
            padding: 2rem; 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        ">
            <h1 style="font-size: 3.5rem; margin: 0; font-weight: bold;">{current_losses:,.0f}₽</h1>
            <p style="font-size: 1.4rem; margin: 10px 0;">Общие потери за период</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_scenario_metrics(metrics: dict):
        """Рендерит метрики what-if"""
        st.markdown("### 📊 Потенциальная экономия (What-if)")
        
        cols = st.columns(5)
        
        with cols[0]:
            st.metric(
                label="A-класс",
                value=f"{metrics.get('savings_a', 0):,.0f}₽",
                delta=f"-{metrics.get('scenarios', {}).get('reduce_a', 0)}%"
            )
        
        with cols[1]:
            st.metric(
                label="Пиковые дни",
                value=f"{metrics.get('savings_peak', 0):,.0f}₽",
                delta=f"-{metrics.get('scenarios', {}).get('reduce_peak', 0)}%"
            )
        
        with cols[2]:
            st.metric(
                label="Топ-магазины (80%)",
                value=f"{metrics.get('savings_store', 0):,.0f}₽",
                delta=f"-{metrics.get('scenarios', {}).get('reduce_top_store', 0)}%"
            )
        
        with cols[3]:
            st.metric(
                label="Итого за период",
                value=f"{metrics.get('total_savings', 0):,.0f}₽"
            )
        
        with cols[4]:
            st.metric(
                label="Годовая экономия",
                value=f"{metrics.get('annual_savings', 0):,.0f}₽"
            )
        
        # ROI если есть инвестиции
        if metrics.get('scenarios', {}).get('investments', 0) > 0:
            roi = metrics.get('roi', 0)
            st.metric(
                label="ROI (возврат инвестиций)",
                value=f"{roi:.1f}%" if roi > 0 else "—",
                delta="Эффективность" if roi > 0 else None
            )