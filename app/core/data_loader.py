# core/data_loader.py
import streamlit as st
import pandas as pd
import numpy as np


class DataLoader:
    @st.cache_data(ttl=3600, show_spinner="Загрузка данных...")
    def load(_self, uploaded_file=None, use_test_data=True) -> pd.DataFrame:
        # _self — это трюк для обхода ошибки хэширования self

        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Поддерживаются только CSV и Excel")
                return pd.DataFrame()
            return df

        if use_test_data:
            return _self._generate_test_data()
        return pd.DataFrame()

    def _generate_test_data(self) -> pd.DataFrame:
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        entities = [f"Entity_{i:03d}" for i in range(1, 21)]
        categories = ["Электроника", "Одежда", "Продукты", "Бытовая техника", "Косметика"]
        data = []
        for date in dates:
            for ent in entities:
                for cat in categories:
                    value = round(np.random.gamma(2, 100) * (1.5 if date.dayofweek >= 5 else 1), 2)
                    data.append({"date": date, "entity": ent, "category": cat, "value": value})
        return pd.DataFrame(data)