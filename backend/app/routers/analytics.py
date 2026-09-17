from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas.analytics import DashboardMetrics, SentimentMetrics, ForecastResponse, ForecastDataPoint
from ..services.analytics_service import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Fetches high-level operational statistics (KPI cards)."""
    try:
        return analytics_service.get_dashboard_metrics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load metrics: {str(e)}")

@router.get("/sentiment", response_model=SentimentMetrics)
def get_sentiment_trends(db: Session = Depends(get_db)):
    """Fetches user feedback satisfaction distributions."""
    try:
        return analytics_service.get_sentiment_metrics(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sentiment: {str(e)}")

@router.get("/forecasting", response_model=ForecastResponse)
def get_ticket_forecast(db: Session = Depends(get_db)):
    """Fetches 7-day time-series projections of support queue volume."""
    try:
        predictions = analytics_service.get_ticket_volume_forecast(db)
        return {"forecast": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run forecaster: {str(e)}")
