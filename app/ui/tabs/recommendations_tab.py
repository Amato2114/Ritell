import streamlit as st
from typing import Dict, Any
import pandas as pd


class RecommendationsTab:
    """Рекомендации и бизнес-инсайты"""

    def render(self, df: pd.DataFrame, metrics: Dict[str, Any], filter_state: Dict[str, Any]):
        st.header("💡 Рекомендации и инсайты")

        total_savings = metrics.get('total_savings', 0)
        annual = metrics.get('annual_savings', 0)
        roi = metrics.get('roi', 0)

        st.success(f"**Потенциальная годовая экономия: {annual:,.0f} ₽** (ROI {roi:.1f}%)")

        st.subheader("Приоритетные действия")

        recs = []

        a_loss = metrics.get('a_class_value', 0)
        if a_loss > 0:
            recs.append(f"🔴 Сосредоточьтесь на **A-классе** — {a_loss:,.0f} ₽ ({(a_loss/metrics.get('current_value',1))*100:.1f}% всего)")

        peak = metrics.get('peak_days_value', 0)
        if peak > 0:
            recs.append(f"📅 Работайте с **пиковыми днями** — {peak:,.0f} ₽ (топ 20% дней)")

        top_ent = metrics.get('top_entity_value', 0)
        if top_ent > 0:
            recs.append(f"🏪 Фокус на **топ-объектах** (80/20) — {top_ent:,.0f} ₽")

        if total_savings > 50000:
            recs.append(f"💰 Инвестируйте до {metrics.get('scenarios',{}).get('investments',50000):,.0f} ₽ — окупаемость {roi:.1f}%")

        for i, rec in enumerate(recs[:5]):
            st.info(rec)

        st.subheader("Что делать дальше")
        st.markdown("""
        1. **A-класс** → внедрить контроль/аудит  
        2. **Пиковые дни** → график смен, камеры, обучение  
        3. **Топ-объекты** → аудит именно этих магазинов/регионов  
        4. Экспортировать отчёт → отправить руководству  
        5. Загрузить новые данные → следить за динамикой
        """)

        # Кнопка экспорта
        if st.button("📤 Скачать полный отчёт Excel"):
            # Здесь можно вызвать ExportManager, если он у тебя есть
            st.success("Отчёт скачан (в реальном проекте — вызов ExportManager)")