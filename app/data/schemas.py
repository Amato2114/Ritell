# data/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import date
import pandas as pd

class FilterState(BaseModel):
    selected_stores: List[str] = Field(default_factory=list)
    selected_categories: List[str] = Field(default_factory=list)
    date_range: Tuple[date, date]
    scenario_a: float = 10.0
    scenario_peak: float = 15.0
    
class Metrics(BaseModel):
    total_losses: float
    category_losses: pd.DataFrame
    store_losses: pd.DataFrame
    anomalies: Optional[pd.DataFrame] = None
    
    class Config:
        arbitrary_types_allowed = True