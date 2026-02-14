import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

class AnalyticsEngine:
    """Универсальный движок аналитики — работает с колонками date / value / entity / category"""

    def calculate_all_metrics(self, df: pd.DataFrame, filter_state: Dict[str, Any]) -> Dict[str, Any]:
        if df.empty or 'value' not in df.columns:
            return {}

        # Основные метрики
        current_value = self._calculate_total_value(df)
        category_losses = self._calculate_category_losses(df)
        entity_losses = self._calculate_entity_losses(df)

        # ABC/XYZ и Pareto (теперь на entity)
        abc_xyz = self._calculate_abc_xyz(df)
        pareto_entity = self._calculate_pareto(df)

        # What-if компоненты
        a_class_value = self._calculate_a_class_value(abc_xyz)
        peak_days_value = self._calculate_peak_days_value(df)
        top_entity_value = self._calculate_top_entity_value(pareto_entity)

        # Сценарии из фильтров
        scenarios = {
            'reduce_a': filter_state.get('reduce_a', 10.0),
            'reduce_peak': filter_state.get('reduce_peak', 15.0),
            'reduce_top_entity': filter_state.get('reduce_top_store', 20.0),  # оставил старый ключ для совместимости
            'investments': filter_state.get('investments', 50000.0)
        }

        # Расчёт экономии
        savings_a = round(a_class_value * scenarios['reduce_a'] / 100)
        savings_peak = round(peak_days_value * scenarios['reduce_peak'] / 100)
        savings_entity = round(top_entity_value * scenarios['reduce_top_entity'] / 100)
        total_savings = savings_a + savings_peak + savings_entity

        # Период для годовой экстраполяции
        date_range = filter_state.get('date_range', (df['date'].min(), df['date'].max()))
        period_days = (date_range[1] - date_range[0]).days + 1 if isinstance(date_range[0], datetime) else 30
        annual_savings = round(total_savings * (365 / period_days)) if period_days else 0

        roi = round(total_savings / scenarios['investments'] * 100, 1) if scenarios['investments'] else 0

        return {
            'current_value': current_value,          # было current_losses
            'category_losses': category_losses,
            'entity_losses': entity_losses,          # было store_losses
            'abc_xyz': abc_xyz,
            'pareto_entity': pareto_entity,          # было pareto_store
            'a_class_value': a_class_value,
            'peak_days_value': peak_days_value,
            'top_entity_value': top_entity_value,
            'scenarios': scenarios,
            'savings_a': savings_a,
            'savings_peak': savings_peak,
            'savings_entity': savings_entity,        # было savings_store
            'total_savings': total_savings,
            'annual_savings': annual_savings,
            'roi': roi,
            'period_days': period_days
        }

    # ====================== ВНУТРЕННИЕ МЕТОДЫ ======================
    def _calculate_total_value(self, df: pd.DataFrame) -> float:
        return float(df['value'].sum()) if 'value' in df.columns else 0.0

    def _calculate_category_losses(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'category' not in df.columns or 'value' not in df.columns:
            return pd.DataFrame()
        cat_loss = df.groupby('category')['value'].sum().reset_index()
        cat_loss = cat_loss.sort_values('value', ascending=False)
        cat_loss['percentage'] = (cat_loss['value'] / cat_loss['value'].sum() * 100).round(1)
        return cat_loss

    def _calculate_entity_losses(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'entity' not in df.columns or 'value' not in df.columns:
            return pd.DataFrame()
        ent_loss = df.groupby('entity')['value'].sum().reset_index()
        ent_loss = ent_loss.sort_values('value', ascending=False)
        ent_loss['percentage'] = (ent_loss['value'] / ent_loss['value'].sum() * 100).round(1)
        return ent_loss

    def _calculate_abc_xyz(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'value' not in df.columns:
            return pd.DataFrame()

        if 'category' in df.columns:
            group_col = 'category'
        elif 'entity' in df.columns:
            group_col = 'entity'
        else:
            group_col = df.columns[0]

        abc_data = df.groupby(group_col)['value'].sum().reset_index()
        abc_data = abc_data.sort_values('value', ascending=False)
        abc_data['cumulative_percentage'] = (abc_data['value'].cumsum() / abc_data['value'].sum() * 100).round(2)

        def assign_abc(row):
            if row['cumulative_percentage'] <= 80: return 'A'
            elif row['cumulative_percentage'] <= 95: return 'B'
            return 'C'

        abc_data['abc_class'] = abc_data.apply(assign_abc, axis=1)
        return abc_data

    def _calculate_pareto(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'entity' not in df.columns or 'value' not in df.columns:
            return pd.DataFrame()
        pareto_data = self._calculate_entity_losses(df)
        if pareto_data.empty:
            return pareto_data
        pareto_data['cumulative_percentage'] = (pareto_data['value'].cumsum() / pareto_data['value'].sum() * 100).round(2)
        pareto_data['is_top_80'] = pareto_data['cumulative_percentage'] <= 80
        return pareto_data

    def _calculate_a_class_value(self, abc_xyz: pd.DataFrame) -> float:
        if abc_xyz.empty or 'abc_class' not in abc_xyz.columns:
            return 0.0
        a_class = abc_xyz[abc_xyz['abc_class'] == 'A']
        return float(a_class['value'].sum()) if 'value' in a_class.columns else 0.0

    def _calculate_peak_days_value(self, df: pd.DataFrame) -> float:
        if 'date' not in df.columns or 'value' not in df.columns:
            return 0.0
        daily = df.groupby('date')['value'].sum().reset_index()
        daily = daily.sort_values('value', ascending=False)
        top_20_count = max(1, int(len(daily) * 0.2))
        return float(daily.head(top_20_count)['value'].sum())

    def _calculate_top_entity_value(self, pareto_entity: pd.DataFrame) -> float:
        if pareto_entity.empty or 'is_top_80' not in pareto_entity.columns:
            return 0.0
        top = pareto_entity[pareto_entity['is_top_80']]
        return float(top['value'].sum()) if 'value' in top.columns else 0.0