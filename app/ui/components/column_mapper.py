import streamlit as st
import pandas as pd
from typing import Dict, Optional

class ColumnMapper:
    """Универсальный маппер колонок — работает с ЛЮБЫМИ данными"""

    ROLES = {
        "date": "📅 Дата (обязательно)",
        "value": "💰 Основная метрика (суммируется: потери, продажи, расходы…)",
        "entity": "🏪 Уровень 1 (магазин / регион / клиент / SKU…)",
        "category": "📦 Уровень 2 (категория / товар / тип…)",
    }

    @staticmethod
    def render(df: pd.DataFrame) -> Optional[Dict[str, str]]:
        if df.empty:
            st.error("Файл пустой")
            return None

        st.sidebar.header("🔗 Назначьте роли колонкам")
        st.sidebar.caption("Авто-детекция уже сработала — просто проверьте")

        auto_map = ColumnMapper._auto_detect(df)
        mapping = {}

        # Список всегда начинается с "не выбрано" → index=0 всегда безопасен
        available_cols = ["— Не выбрано —"] + list(df.columns)

        for role, label in ColumnMapper.ROLES.items():
            default_col = auto_map.get(role)

            # Безопасный расчёт индекса
            if default_col in df.columns:
                try:
                    idx = available_cols.index(default_col)
                except ValueError:
                    idx = 0
            else:
                idx = 0

            selected_col = st.sidebar.selectbox(
                label,
                options=available_cols,
                index=idx,
                key=f"map_{role}"
            )

            if selected_col != "— Не выбрано —":
                mapping[role] = selected_col

        # Проверка обязательных полей
        if "date" not in mapping or "value" not in mapping:
            st.sidebar.error("Обязательно выберите **Дата** и **Основная метрика**")
            return None

        # Дополнительные фильтры (опционально)
        used_cols = set(mapping.values())
        extra_cols = [c for c in df.columns if c not in used_cols]
        if extra_cols:
            st.sidebar.multiselect(
                "Дополнительные фильтры",
                extra_cols,
                default=extra_cols[:min(4, len(extra_cols))],
                key="extra_filters"
            )

        return mapping

    @staticmethod
    def apply(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        df = df.copy()
        rename_map = {v: k for k, v in mapping.items()}
        df = df.rename(columns=rename_map)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)

        # Убираем строки без ключевых колонок
        key_cols = [c for c in ["date", "value"] if c in df.columns]
        if key_cols:
            df = df.dropna(subset=key_cols)

        return df.reset_index(drop=True)

    @staticmethod
    def _auto_detect(df: pd.DataFrame) -> Dict[str, str]:
        """Автоматически угадывает колонки по типичным именам"""
        lower_cols = {col.lower().strip(): col for col in df.columns}
        detected = {}

        date_patterns = ['date', 'time', 'day', 'order_date', 'transaction_date', 'дата']
        value_patterns = ['amount', 'value', 'loss', 'revenue', 'sales', 'cost', 'qty', 'quantity', 'сумма', 'потери']
        entity_patterns = ['store', 'shop', 'region', 'client', 'customer', 'id', 'sku', 'магазин']
        cat_patterns = ['category', 'group', 'product', 'type', 'item', 'категория', 'товар']

        for pattern in date_patterns:
            if pattern in lower_cols:
                detected["date"] = lower_cols[pattern]
                break

        for pattern in value_patterns:
            if pattern in lower_cols:
                detected["value"] = lower_cols[pattern]
                break

        for pattern in entity_patterns:
            if pattern in lower_cols:
                detected["entity"] = lower_cols[pattern]
                break

        for pattern in cat_patterns:
            if pattern in lower_cols:
                detected["category"] = lower_cols[pattern]
                break

        return detected