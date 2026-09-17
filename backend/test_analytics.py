import os
import sys
from datetime import datetime, timedelta, timezone

# Adjust Python path to import app correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.models.ticket import Ticket
from app.services.analytics_service import analytics_service

def run_analytics_test():
    print("Initializing test database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Clean Database
    print("Cleaning database tables...")
    db.query(Ticket).delete()
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.commit()
    
    # 2. Seed Mock Users
    print("Seeding mock users (clients and support team)...")
    c1 = User(name="User A", email="usera@example.com", role="customer")
    c2 = User(name="User B", email="userb@example.com", role="customer")
    a1 = User(name="Agent Bob", email="bob@example.com", role="agent")
    db.add_all([c1, c2, a1])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(a1)
    
    # 3. Seed Chat Sessions & Messages (to test Sentiment metrics)
    print("Seeding support chats and sentiment markers...")
    
    # Chat 1: Positive sentiment
    s1 = ChatSession(user_id=c1.id, status="resolved")
    db.add(s1)
    db.commit()
    db.refresh(s1)
    
    m1 = ChatMessage(session_id=s1.id, sender="user", content="Hello, how do I setup my email account?", sentiment="neutral")
    m2 = ChatMessage(session_id=s1.id, sender="assistant", content="You can setup email by going to options...", sentiment="neutral")
    m3 = ChatMessage(session_id=s1.id, sender="user", content="That worked perfectly, thank you! Great tool!", sentiment="positive")
    db.add_all([m1, m2, m3])
    
    # Chat 2: Negative sentiment
    s2 = ChatSession(user_id=c2.id, status="escalated")
    db.add(s2)
    db.commit()
    db.refresh(s2)
    
    m4 = ChatMessage(session_id=s2.id, sender="user", content="The login page throws internal server error. Broken website", sentiment="negative")
    db.add(m4)
    db.commit()

    # 4. Seed Support Tickets (to test Dashboard & Forecasting metrics)
    print("Seeding historical support tickets...")
    now = datetime.now(timezone.utc)
    
    # Ticket 1: Resolved in 4 hours
    t1 = Ticket(
        session_id=s1.id,
        user_id=c1.id,
        title="Email Setup Request",
        description="Help client configure their IMAP settings.",
        category="general",
        priority="low",
        status="resolved",
        assigned_agent_id=a1.id,
        created_at=now - timedelta(hours=6),
        resolved_at=now - timedelta(hours=2)
    )
    
    # Ticket 2: Resolved in 8 hours
    t2 = Ticket(
        user_id=c2.id,
        title="Downtime outage report",
        description="Website returns 500 server error on login attempt.",
        category="technical",
        priority="critical",
        status="resolved",
        assigned_agent_id=a1.id,
        created_at=now - timedelta(hours=12),
        resolved_at=now - timedelta(hours=4)
    )
    
    # Ticket 3: Still Open
    t3 = Ticket(
        session_id=s2.id,
        user_id=c2.id,
        title="Login server downtime",
        description="Web service crashed node down",
        category="technical",
        priority="high",
        status="open",
        created_at=now - timedelta(hours=1)
    )
    
    db.add_all([t1, t2, t3])
    db.commit()

    # 5. Run KPI Analytics Validation
    print("\n--- KPI Metric Dashboard Results ---")
    kpis = analytics_service.get_dashboard_metrics(db)
    print(f"Total Chat Sessions logged: {kpis['total_chats']} (Expected: 2)")
    print(f"Active Open Tickets in Queue: {kpis['open_tickets']} (Expected: 1)")
    print(f"Registered User Base: {kpis['user_count']} (Expected: 3)")
    print(f"Average Ticket Resolution speed: {kpis['avg_resolution_time_hours']} hours (Expected: 6.0)")
    
    # Assert correctness
    assert kpis['total_chats'] == 2, "Chat count mismatch"
    assert kpis['open_tickets'] == 1, "Open tickets mismatch"
    assert kpis['avg_resolution_time_hours'] == 6.0, "Avg resolution calculation error"

    # 6. Run Sentiment Analytics Validation
    print("\n--- Sentiment Metric Aggregations ---")
    sentiment = analytics_service.get_sentiment_metrics(db)
    print(f"User Positive Messages: {sentiment['positive']}")
    print(f"User Neutral Messages: {sentiment['neutral']}")
    print(f"User Negative Messages: {sentiment['negative']}")
    print(f"Ratios: Positive={sentiment['positive_ratio']:.2%}, Neutral={sentiment['neutral_ratio']:.2%}, Negative={sentiment['negative_ratio']:.2%}")
    
    assert sentiment['positive'] == 1, "Positive count mismatch"
    assert sentiment['negative'] == 1, "Negative count mismatch"

    # 7. Run Predictive Time-Series Forecasting
    print("\n--- Ticket Volume 7-Day Forecasting Projections ---")
    forecast = analytics_service.get_ticket_volume_forecast(db)
    print("Projected Queue workloads for the next 7 days:")
    for point in forecast:
        # Determine day of week for display
        date_obj = datetime.strptime(point['date'], "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")
        print(f" - {point['date']} ({day_of_week}): {point['predicted_tickets']} tickets predicted")

    # 8. Clean up
    print("\nCleaning up test database records...")
    db.query(Ticket).delete()
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.commit()
    db.close()
    
    print("\n--- Phase 4 Analytics & Forecasting Verification Complete! ---")

if __name__ == "__main__":
    run_analytics_test()
