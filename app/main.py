import streamlit as st
import pandas as pd
from core.data_loader import DataLoader
from core.analytics_engine import AnalyticsEngine
from ui.components.column_mapper import ColumnMapper
from ui.components.filter_manager import FilterManager
from ui.tabs.tab_manager import TabManager

# === DARK MODE ===
if "theme" not in st.session_state:
    st.session_state.theme = "light"

st.sidebar.toggle("🌙 Тёмная тема", value=st.session_state.theme == "dark", key="theme_toggle")
if st.session_state.get("theme_toggle") != (st.session_state.theme == "dark"):
    st.session_state.theme = "dark" if st.session_state.theme_toggle else "light"
    st.rerun()

# === CSS ===
st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{ background-color: {'#0F172A' if st.session_state.theme == 'dark' else '#FFFFFF'} !important; }}
    .stMetric, .stPlotlyChart, .stDataFrame {{ border-radius: 16px; padding: 1rem; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Universal Analytics Dashboard 2026")
st.caption("Загружай любые данные — дашборд сам всё разберёт")

uploaded = st.sidebar.file_uploader("CSV / Excel", type=["csv", "xlsx", "xls"])

loader = DataLoader()
raw_df = loader.load(uploaded, use_test_data=uploaded is None)

if not raw_df.empty:
    if "column_mapping" not in st.session_state or st.sidebar.button("🔄 Пересопоставить колонки"):
        mapping = ColumnMapper.render(raw_df)
        if mapping:
            st.session_state.column_mapping = mapping
            st.session_state.df = ColumnMapper.apply(raw_df, mapping)
            st.success("✅ Колонки сопоставлены!")
            st.rerun()

    if "df" in st.session_state:
        df = st.session_state.df
        filter_manager = FilterManager()
        filter_state = filter_manager.render_sidebar(df)
        filtered_df = filter_manager.apply(df, filter_state)

        engine = AnalyticsEngine()
        metrics = engine.calculate_all_metrics(filtered_df, filter_state)

        tab_manager = TabManager()
        tab_manager.render_all(filtered_df, metrics, filter_state)
    else:
        st.info("Назначь роли колонкам в сайдбаре ↑")
else:
    st.warning("Загрузи файл или используй демо-данные")