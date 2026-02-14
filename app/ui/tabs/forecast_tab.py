# app/ui/tabs/forecast_tab.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go   # ← обязательно для go.Figure()
import numpy as np
from typing import Dict, Any


class ForecastTab:
    """Вкладка прогнозирования"""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("🔮 Прогнозирование")

        if 'date' not in df.columns or df.empty:
            st.warning("Нужны данные с датами")
            return

        method = st.selectbox(
            "Метод прогнозирования",
            ["Скользящее среднее", "Экспоненциальное сглаживание", "Простой тренд"]
        )
        forecast_days = st.slider("Прогноз на дней вперёд", 7, 90, 30)

        # Подготовка ежедневных данных
        daily = df.groupby('date')['value'].sum().reset_index()
        daily_series = daily.set_index('date')['value']

        if len(daily_series) < 14:
            st.warning(f"Мало данных — всего {len(daily_series)} дней. Нужно минимум 14.")
            return

        st.subheader("Исходный временной ряд")
        fig_actual = px.line(
            daily,
            x='date',
            y='value',
            title='Фактические значения'
        )
        st.plotly_chart(fig_actual, use_container_width=True)

        # Вычисление прогноза
        if method == "Скользящее среднее":
            forecast = self._moving_average_forecast(daily_series, forecast_days)
        elif method == "Экспоненциальное сглаживание":
            forecast = self._exponential_smoothing_forecast(daily_series, forecast_days)
        else:
            forecast = self._simple_trend_forecast(daily_series, forecast_days)

        self._visualize_forecast(daily_series, forecast, method, forecast_days)

    def _moving_average_forecast(self, series: pd.Series, days: int) -> np.ndarray:
        window = st.slider("Окно среднего (дней)", 3, 30, 7)
        ma = series.rolling(window=window, min_periods=1).mean()
        last_value = ma.iloc[-1]
        return np.full(days, last_value)

    def _exponential_smoothing_forecast(self, series: pd.Series, days: int) -> np.ndarray:
        alpha = st.slider("Alpha (0.1–1.0)", 0.1, 1.0, 0.3, 0.05)
        smoothed = series.ewm(alpha=alpha, adjust=False).mean()
        last_value = smoothed.iloc[-1]
        return np.full(days, last_value)

    def _simple_trend_forecast(self, series: pd.Series, days: int) -> np.ndarray:
        x = np.arange(len(series))
        coeffs = np.polyfit(x, series.values, 1)
        future_x = np.arange(len(series), len(series) + days)
        return coeffs[0] * future_x + coeffs[1]

    def _visualize_forecast(self, series: pd.Series, forecast: np.ndarray, method: str, days: int):
        last_date = series.index[-1]
        future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines',
            name='Факт',
            line=dict(color='#EF4444')
        ))

        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast,
            mode='lines+markers',
            name='Прогноз',
            line=dict(color='#10B981', dash='dash')
        ))

        fig.update_layout(
            title=f"Прогноз на {days} дней ({method})",
            xaxis_title="Дата",
            yaxis_title="Значение",
            height=500,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)