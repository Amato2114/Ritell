# app/ui/layout.py
import streamlit as st


class DashboardLayout:
    """Управление layout дашборда"""
    
    def __init__(self):
        self.theme = self._setup_theme()
    
    def _setup_theme(self):
        """Настройка темы"""
        # Можно добавить переключение светлой/тёмной темы
        return {
            'primary_color': '#e74c3c',
            'secondary_color': '#3498db',
            'bg_color': '#ffffff',
            'text_color': '#2c3e50'
        }