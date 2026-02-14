# app/ui/components/filter_manager.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

class FilterManager:
    def __init__(self):
        self.default_scenarios = {
            'reduce_a': 10.0,
            'reduce_peak': 15.0,
            'reduce_top_entity': 20.0,
            'investments': 50000.0
        }

    def render_sidebar(self, df: pd.DataFrame) -> Dict[str, Any]:
        filter_state = {}

        st.sidebar.header("🔗 Фильтры")

        if 'entity' in df.columns:
            entities = sorted(df['entity'].dropna().unique().tolist())
            selected = st.sidebar.multiselect(
                "🏪 Уровень 1 (магазин / регион / клиент)",
                entities,
                default=entities[:8] if len(entities) > 8 else entities
            )
            filter_state['selected_entities'] = selected

        if 'category' in df.columns:
            cats = sorted(df['category'].dropna().unique().tolist())
            selected = st.sidebar.multiselect(
                "📦 Уровень 2 (категория / товар)",
                cats,
                default=cats[:6] if len(cats) > 6 else cats
            )
            filter_state['selected_categories'] = selected

        if 'date' in df.columns:
            min_d, max_d = df['date'].min(), df['date'].max()
            date_range = st.sidebar.date_input(
                "📅 Диапазон дат",
                value=(min_d, max_d),
                min_value=min_d,
                max_value=max_d
            )
            if len(date_range) == 2:
                filter_state['date_range'] = (date_range[0], date_range[1])

        st.sidebar.divider()
        st.sidebar.header("🔮 What-if сценарии")

        filter_state['reduce_a'] = st.sidebar.slider(
            "Снижение A-класса (%)", 0.0, 100.0, self.default_scenarios['reduce_a'], step=1.0
        )
        filter_state['reduce_peak'] = st.sidebar.slider(
            "Снижение в пиковые дни (%)", 0.0, 100.0, self.default_scenarios['reduce_peak'], step=1.0
        )
        filter_state['reduce_top_entity'] = st.sidebar.slider(
            "Снижение в топ-объектах (80%) (%)", 0.0, 100.0, self.default_scenarios['reduce_top_entity'], step=1.0
        )
        filter_state['investments'] = st.sidebar.number_input(
            "Инвестиции (₽)", 0.0, value=self.default_scenarios['investments'], step=10000.0
        )

        if st.sidebar.button("🔄 Сбросить всё"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        return filter_state

    def apply(self, df: pd.DataFrame, filter_state: Dict[str, Any]) -> pd.DataFrame:
        filtered = df.copy()

        if filter_state.get('selected_entities') and 'entity' in filtered.columns:
            filtered = filtered[filtered['entity'].isin(filter_state['selected_entities'])]

        if filter_state.get('selected_categories') and 'category' in filtered.columns:
            filtered = filtered[filtered['category'].isin(filter_state['selected_categories'])]

        if 'date' in filtered.columns and 'date_range' in filter_state:
            start, end = filter_state['date_range']
            mask = (filtered['date'] >= pd.Timestamp(start)) & (filtered['date'] <= pd.Timestamp(end))
            filtered = filtered[mask]

        return filtered.reset_index(drop=True)