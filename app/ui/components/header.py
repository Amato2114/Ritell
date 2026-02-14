# app/ui/components/header.py
import streamlit as st


class Header:
    """Компонент заголовка"""
    
    @staticmethod
    def render():
        """Рендерит заголовок дашборда"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="main-header">
            <h1>📉 RetailLoss Sentinel Pro</h1>
            <p>AI-powered аналитика потерь в ритейле | Real-time дашборд</p>
        </div>
        """, unsafe_allow_html=True)