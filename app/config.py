"""
Конфигурация приложения RetailLoss Sentinel.
Настройки можно переопределить через переменные окружения.
"""
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import timedelta

@dataclass
class AppConfig:
    """Основная конфигурация приложения."""
    
    # ===== Настройки Streamlit =====
    STREAMLIT_PORT: int = 8502
    STREAMLIT_THEME: str = "light"
    STREAMLIT_SERVER_HEADLESS: bool = False
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE: int = 200  # MB
    STREAMLIT_BROWSER_GATHER_USAGE_STATS: bool = False
    
    # ===== Настройки данных =====
    DEFAULT_TEST_DATA_DAYS: int = 365
    DEFAULT_STORE_COUNT: int = 20
    DEFAULT_CATEGORIES: List[str] = None
    MAX_FILE_SIZE_MB: int = 100
    SUPPORTED_FILE_TYPES: List[str] = None
    
    # ===== Настройки аналитики =====
    ABC_A_THRESHOLD: float = 80.0
    ABC_B_THRESHOLD: float = 95.0
    PARETO_THRESHOLD: float = 80.0
    ANOMALY_CONTAMINATION: float = 0.1
    FORECAST_DAYS: int = 30
    
    # ===== Настройки кэширования =====
    CACHE_TTL_DATA_LOADER: int = 3600  # 1 час
    CACHE_TTL_ANALYTICS: int = 300     # 5 минут
    CACHE_TTL_TEST_DATA: int = 600     # 10 минут
    
    # ===== Настройки UI =====
    CHART_HEIGHT: int = 500
    COLOR_SCHEME: str = "reds"
    DEFAULT_SCENARIOS: Dict[str, float] = None
    ENABLE_DARK_MODE: bool = True
    
    # ===== Настройки безопасности =====
    ENABLE_CSRF_PROTECTION: bool = False
    ALLOWED_FILE_EXTENSIONS: List[str] = None
    
    def __post_init__(self):
        """Инициализация значений по умолчанию после создания."""
        if self.DEFAULT_CATEGORIES is None:
            self.DEFAULT_CATEGORIES = [
                'Электроника', 'Одежда', 'Продукты', 
                'Бытовая техника', 'Косметика', 'Спорттовары'
            ]
        
        if self.SUPPORTED_FILE_TYPES is None:
            self.SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'parquet']
        
        if self.DEFAULT_SCENARIOS is None:
            self.DEFAULT_SCENARIOS = {
                'reduce_a': 10.0,
                'reduce_peak': 15.0,
                'reduce_top_store': 20.0,
                'investments': 50000.0
            }
        
        if self.ALLOWED_FILE_EXTENSIONS is None:
            self.ALLOWED_FILE_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.parquet']
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Создаёт конфигурацию из переменных окружения."""
        env_config = {}
        
        # Чтение всех переменных окружения с префиксом RETAIL_
        for key, value in os.environ.items():
            if key.startswith('RETAIL_'):
                config_key = key[7:]  # Убираем префикс RETAIL_
                
                # Преобразование типов
                if value.isdigit():
                    env_config[config_key] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    env_config[config_key] = float(value)
                elif value.lower() in ('true', 'false'):
                    env_config[config_key] = value.lower() == 'true'
                else:
                    env_config[config_key] = value
        
        return cls(**env_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию в виде словаря."""
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }
    
    def validate(self) -> List[str]:
        """Проверяет корректность конфигурации."""
        errors = []
        
        if self.STREAMLIT_PORT < 1024 or self.STREAMLIT_PORT > 65535:
            errors.append(f"Порт должен быть в диапазоне 1024-65535: {self.STREAMLIT_PORT}")
        
        if self.ABC_A_THRESHOLD >= self.ABC_B_THRESHOLD:
            errors.append(f"ABC_A_THRESHOLD ({self.ABC_A_THRESHOLD}) должен быть меньше ABC_B_THRESHOLD ({self.ABC_B_THRESHOLD})")
        
        if self.ANOMALY_CONTAMINATION <= 0 or self.ANOMALY_CONTAMINATION >= 1:
            errors.append(f"ANOMALY_CONTAMINATION должен быть между 0 и 1: {self.ANOMALY_CONTAMINATION}")
        
        return errors

# Глобальный экземпляр конфигурации
config = AppConfig.from_env()