import streamlit as st

from .overview_tab import OverviewTab
from .charts_tab import ChartsTab
from .anomalies_tab import AnomaliesTab
from .abc_pareto_tab import ABCTab
from .forecast_tab import ForecastTab
from .recommendations_tab import RecommendationsTab


class TabManager:
    """Фасад для управления всеми вкладками дашборда."""

    def __init__(self):
        self.tabs = {
            'overview': OverviewTab(),
            'charts': ChartsTab(),
            'anomalies': AnomaliesTab(),
            'abc': ABCTab(),
            'forecast': ForecastTab(),
            'recommendations': RecommendationsTab()
        }

    def render_all(self, df, metrics, filter_state):
        """Рендерит все вкладки."""
        tab_names = [
            "📊 Обзор",
            "📈 Графики",
            "🔍 Аномалии",
            "📊 ABC / Pareto",
            "🔮 Прогноз",
            "💡 Рекомендации"
        ]

        tabs = st.tabs(tab_names)

        with tabs[0]:
            self.tabs['overview'].render(df, metrics, filter_state)

        with tabs[1]:
            self.tabs['charts'].render(df, metrics, filter_state)

        with tabs[2]:
            self.tabs['anomalies'].render(df, metrics, filter_state)

        with tabs[3]:
            self.tabs['abc'].render(df, metrics, filter_state)

        with tabs[4]:
            self.tabs['forecast'].render(df, metrics, filter_state)

        with tabs[5]:
            self.tabs['recommendations'].render(df, metrics, filter_state)