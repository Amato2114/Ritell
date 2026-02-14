import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any, Optional


class FilterManager:
    """Управление фильтрами и сценариями what-if"""
    
    def __init__(self):
        self.default_scenarios = {
            'reduce_a': 10.0,
            'reduce_peak': 15.0,
            'reduce_top_store': 20.0,
            'investments': 50000.0
        }
    
    def render_sidebar(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Рендерит все фильтры в сайдбаре"""
        filter_state = {}
        
        # Секция фильтров
        st.sidebar.header("🔍 Фильтры")
        
        # Фильтр по магазинам
        if 'store_id' in df.columns:
            stores = sorted(df['store_id'].unique().tolist())
            selected_stores = st.sidebar.multiselect(
                "Магазины",
                stores,
                default=stores[:5] if len(stores) > 5 else stores,
                help="Выберите магазины для анализа"
            )
            filter_state['selected_stores'] = selected_stores
        else:
            filter_state['selected_stores'] = []
        
        # Фильтр по категориям
        if 'category' in df.columns:
            categories = sorted(df['category'].unique().tolist())
            selected_categories = st.sidebar.multiselect(
                "Категории",
                categories,
                default=categories[:5] if len(categories) > 5 else categories,
                help="Выберите категории товаров"
            )
            filter_state['selected_categories'] = selected_categories
        else:
            filter_state['selected_categories'] = []
        
        # Фильтр по датам
        if 'date' in df.columns:
            min_date = df['date'].min()
            max_date = df['date'].max()
            date_range = st.sidebar.date_input(
                "Диапазон дат",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                filter_state['date_range'] = (date_range[0], date_range[1])
            else:
                filter_state['date_range'] = (min_date, max_date)
        else:
            filter_state['date_range'] = (datetime.now() - timedelta(days=30), datetime.now())
        
        st.sidebar.divider()
        st.sidebar.header("📈 Сценарии (What-if)")
        
        # Все слайдеры с float типами
        reduce_a = st.sidebar.slider(
            "Снижение потерь по A-классу (%)",
            0.0, 100.0, float(self.default_scenarios['reduce_a']),
            step=1.0,
            help="Предполагаемое снижение потерь по товарам A-класса"
        )
        filter_state['reduce_a'] = float(reduce_a)
        
        reduce_peak = st.sidebar.slider(
            "Снижение потерь в пиковые дни (%)",
            0.0, 100.0, float(self.default_scenarios['reduce_peak']),
            step=1.0,
            help="Предполагаемое снижение потерь в дни с максимальными потерями"
        )
        filter_state['reduce_peak'] = float(reduce_peak)
        
        reduce_top_store = st.sidebar.slider(
            "Снижение потерь в топ-магазинах (80% потерь) (%)",
            0.0, 100.0, float(self.default_scenarios['reduce_top_store']),
            step=1.0,
            help="Предполагаемое снижение потерь в магазинах, дающих 80% потерь"
        )
        filter_state['reduce_top_store'] = float(reduce_top_store)
        
        investments = st.sidebar.number_input(
            "Инвестиции (руб.)",
            min_value=0.0,
            value=float(self.default_scenarios['investments']),
            step=10000.0,
            help="Объем планируемых инвестиций"
        )
        filter_state['investments'] = float(investments)
        
        if st.sidebar.button("🔄 Сбросить фильтры"):
            for key in ['selected_stores', 'selected_categories']:
                if key in filter_state:
                    filter_state[key] = []
            filter_state.update(self.default_scenarios)
            st.rerun()
        
        return filter_state
    
    def apply(self, df: pd.DataFrame, filter_state: Dict[str, Any]) -> pd.DataFrame:
        """Применяет фильтры к DataFrame"""
        filtered_df = df.copy()
        
        if filter_state['selected_stores'] and 'store_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['store_id'].isin(filter_state['selected_stores'])]
        
        if filter_state['selected_categories'] and 'category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['category'].isin(filter_state['selected_categories'])]
        
        if 'date' in filtered_df.columns and 'date_range' in filter_state:
            start_date, end_date = filter_state['date_range']
            filtered_df['date'] = pd.to_datetime(filtered_df['date'])
            mask = (filtered_df['date'] >= pd.Timestamp(start_date)) & \
                   (filtered_df['date'] <= pd.Timestamp(end_date))
            filtered_df = filtered_df[mask]
        
        return filtered_df
    
    def get_scenarios(self, filter_state: Dict[str, Any]) -> Dict[str, float]:
        """Извлекает сценарии из состояния фильтров"""
        return {
            'reduce_a': filter_state.get('reduce_a', self.default_scenarios['reduce_a']),
            'reduce_peak': filter_state.get('reduce_peak', self.default_scenarios['reduce_peak']),
            'reduce_top_store': filter_state.get('reduce_top_store', self.default_scenarios['reduce_top_store']),
            'investments': filter_state.get('investments', self.default_scenarios['investments'])
        }