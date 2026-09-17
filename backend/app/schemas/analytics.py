from pydantic import BaseModel
from typing import List

class DashboardMetrics(BaseModel):
    total_chats: int
    open_tickets: int
    avg_resolution_time_hours: float
    user_count: int

class SentimentMetrics(BaseModel):
    positive: int
    neutral: int
    negative: int
    positive_ratio: float
    neutral_ratio: float
    negative_ratio: float

class ForecastDataPoint(BaseModel):
    date: str
    predicted_tickets: int

class ForecastResponse(BaseModel):
    forecast: List[ForecastDataPoint]
