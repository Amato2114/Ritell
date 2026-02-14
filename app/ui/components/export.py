# app/ui/components/export.py
import pandas as pd
import io
import streamlit as st
from datetime import datetime

class ExportManager:
    @staticmethod
    def generate_excel_report(df, metrics):
        """Генерирует Excel-отчёт из DataFrame и рассчитанных метрик."""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Основные данные
            df.to_excel(writer, sheet_name='Исходные данные', index=False)
            
            # Метрики
            if not metrics.get('category_losses', pd.DataFrame()).empty:
                metrics['category_losses'].to_excel(writer, sheet_name='По категориям', index=False)
            
            if not metrics.get('store_losses', pd.DataFrame()).empty:
                metrics['store_losses'].to_excel(writer, sheet_name='По магазинам', index=False)
            
            if not metrics.get('abc_xyz', pd.DataFrame()).empty:
                metrics['abc_xyz'].to_excel(writer, sheet_name='ABC-XYZ', index=False)
            
            # Сценарии What-if
            scenarios_df = pd.DataFrame({
                'Сценарий': ['A-класс', 'Пиковые дни', 'Топ-магазины (80%)', 'Итого'],
                'Снижение %': [
                    metrics.get('scenarios', {}).get('reduce_a', 0),
                    metrics.get('scenarios', {}).get('reduce_peak', 0),
                    metrics.get('scenarios', {}).get('reduce_top_store', 0),
                    '-'
                ],
                'Экономия ₽': [
                    metrics.get('savings_a', 0),
                    metrics.get('savings_peak', 0),
                    metrics.get('savings_store', 0),
                    metrics.get('total_savings', 0)
                ]
            })
            scenarios_df.to_excel(writer, sheet_name='What-if', index=False)
        
        buffer.seek(0)
        
        # Кнопка скачивания в Streamlit
        st.download_button(
            '📥 Скачать полный отчёт Excel',
            data=buffer,
            file_name=f'RetailLoss_Report_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )