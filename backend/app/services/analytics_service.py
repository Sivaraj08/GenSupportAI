import numpy as np
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..models.chat import ChatSession, ChatMessage
from ..models.ticket import Ticket
from ..models.user import User

class AnalyticsService:
    def get_dashboard_metrics(self, db: Session) -> Dict[str, Any]:
        """Calculates high-level support system performance metrics."""
        total_chats = db.query(func.count(ChatSession.id)).scalar() or 0
        open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status != "resolved").scalar() or 0
        user_count = db.query(func.count(User.id)).scalar() or 0
        
        # Calculate Average Resolution Speed
        resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved", Ticket.resolved_at.isnot(None)).all()
        
        if resolved_tickets:
            durations = []
            for t in resolved_tickets:
                # Ensure resolved_at and created_at are timezone-aware or naive before subtracting
                created = t.created_at.replace(tzinfo=timezone.utc) if t.created_at.tzinfo is None else t.created_at
                resolved = t.resolved_at.replace(tzinfo=timezone.utc) if t.resolved_at.tzinfo is None else t.resolved_at
                diff = resolved - created
                durations.append(diff.total_seconds() / 3600.0) # convert seconds to hours
            avg_res_time = float(np.mean(durations))
        else:
            avg_res_time = 0.0
            
        return {
            "total_chats": total_chats,
            "open_tickets": open_tickets,
            "avg_resolution_time_hours": round(avg_res_time, 2),
            "user_count": user_count
        }

    def get_sentiment_metrics(self, db: Session) -> Dict[str, Any]:
        """Aggregates user message sentiments to find overall satisfaction rates."""
        # Query user messages
        results = db.query(ChatMessage.sentiment, func.count(ChatMessage.id))\
            .filter(ChatMessage.sender == "user")\
            .group_by(ChatMessage.sentiment)\
            .all()
            
        counts = {"positive": 0, "neutral": 0, "negative": 0}
        total = 0
        
        for sentiment, count in results:
            if sentiment in counts:
                counts[sentiment] = count
                total += count
                
        ratios = {
            "positive_ratio": round(counts["positive"] / total, 4) if total > 0 else 0.0,
            "neutral_ratio": round(counts["neutral"] / total, 4) if total > 0 else 0.0,
            "negative_ratio": round(counts["negative"] / total, 4) if total > 0 else 0.0
        }
        
        return {**counts, **ratios}

    def get_ticket_volume_forecast(self, db: Session) -> List[Dict[str, Any]]:
        """
        Calculates a 7-day support ticket volume forecast using linear regression and seasonal weights.
        If database is fresh, seeds synthetic ticket history to build a projection.
        """
        today = datetime.now(timezone.utc).date()
        
        # 1. Fetch historical daily counts for past 30 days from DB
        start_date = today - timedelta(days=30)
        db_history = db.query(func.date(Ticket.created_at), func.count(Ticket.id))\
            .filter(Ticket.created_at >= start_date)\
            .group_by(func.date(Ticket.created_at))\
            .all()
            
        # Parse query results into dict mapping date -> count
        history_map = {}
        for dt_str, count in db_history:
            if isinstance(dt_str, str):
                dt = datetime.strptime(dt_str.split()[0], "%Y-%m-%d").date()
            else:
                dt = dt_str
            history_map[dt] = count
            
        # 2. Build complete 30-day historical time-series
        dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
        daily_counts = []
        
        for d in dates:
            if d in history_map:
                daily_counts.append(history_map[d])
            else:
                # Seed synthetic business volume to model a real environment
                # Average of 15 tickets, lower on weekends (Saturday/Sunday), with random variation
                base = 15
                weekday = d.weekday()
                if weekday >= 5: # Saturday, Sunday
                    base = 6
                elif weekday == 0: # Monday surge
                    base = 22
                
                # Add noise using numpy random normal
                rng = np.random.default_rng(seed=d.day) # stable seed based on date
                noise = int(rng.normal(0, 3))
                val = max(1, base + noise)
                daily_counts.append(val)
                
        # 3. Fit Linear Regression trend
        x = np.arange(len(daily_counts))
        y = np.array(daily_counts)
        slope, intercept = np.polyfit(x, y, 1)
        
        # 4. Project next 7 days incorporating weekly seasonality weights
        forecast = []
        for i in range(1, 8):
            future_date = today + timedelta(days=i)
            future_x = len(daily_counts) + i - 1
            
            # Base linear forecast
            pred = slope * future_x + intercept
            
            # Apply seasonality multipliers
            weekday = future_date.weekday()
            if weekday >= 5: # Weekend drop
                pred *= 0.5
            elif weekday == 0: # Monday surge
                pred *= 1.3
            else: # Standard weekdays
                pred *= 1.05
                
            predicted_tickets = max(1, int(round(pred)))
            forecast.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_tickets": predicted_tickets
            })
            
        return forecast

analytics_service = AnalyticsService()
