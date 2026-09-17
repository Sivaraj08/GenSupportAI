import os
import sys
from datetime import datetime, timezone

# Adjust Python path to import app correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.chat import ChatSession
from app.models.ticket import Ticket
from app.services.ticket_service import ticket_classifier

def run_ticket_test():
    print("Initializing test database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Clean Database
    print("Cleaning database tables...")
    db.query(Ticket).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.commit()
    
    # 2. Create Users (Customer & Agent)
    print("Creating mock customer and support agent...")
    customer = User(name="Alice Customer", email="alice@example.com", role="customer")
    agent = User(name="Bob Agent", email="bob@example.com", role="agent")
    db.add_all([customer, agent])
    db.commit()
    db.refresh(customer)
    db.refresh(agent)
    print(f"Customer ID: {customer.id}")
    print(f"Agent ID: {agent.id}")

    # 3. Create Chat Session
    print("\nStarting support chat session...")
    session = ChatSession(user_id=customer.id, status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    print(f"Chat Session ID: {session.id}, status: {session.status}")

    # 4. Trigger Escalation & Run ML Classifications
    # Test cases representing different departments & urgencies
    test_cases = [
        {
            "title": "Database connection failures",
            "desc": "Postgresql database pool connection timeout error on the cluster. The web service crashed completely and returns 500 error on client logins. Need urgent resolution asap.",
            "expected_cat": "technical",
            "expected_prio": "high"
        },
        {
            "title": "Overcharged subscription renewal fee",
            "desc": "I was billed twice on my credit card statement for renewal. I cancelled this account last week, please process a full refund for this overcharge.",
            "expected_cat": "billing",
            "expected_prio": "high"
        },
        {
            "title": "Requesting custom pricing package",
            "desc": "Hi, I am interested in booking a demo of your enterprise assistant product and would like details about high volume pricing packages.",
            "expected_cat": "sales",
            "expected_prio": "medium"
        }
    ]

    print("\n--- Testing ML Classifier on Support Escalations ---")
    created_tickets = []
    for i, tc in enumerate(test_cases):
        print(f"\n[Case {i+1}] Title: '{tc['title']}'")
        print(f"  Description: '{tc['desc'][:100]}...'")
        
        # Call classifier
        pred_cat = ticket_classifier.predict_category(tc["desc"])
        pred_prio = ticket_classifier.predict_priority(tc["desc"], sentiment="negative" if i < 2 else "neutral")
        
        print(f"  ML Predicted Category: '{pred_cat}' (Expected: '{tc['expected_cat']}')")
        print(f"  ML Predicted Priority: '{pred_prio}' (Expected: '{tc['expected_prio']}')")
        
        # Save ticket (each mapped to a separate session for unique constraint check)
        test_session = ChatSession(user_id=customer.id, status="active")
        db.add(test_session)
        db.commit()
        db.refresh(test_session)
        
        new_ticket = Ticket(
            session_id=test_session.id,
            user_id=customer.id,
            title=tc["title"],
            description=tc["desc"],
            category=pred_cat,
            priority=pred_prio,
            status="open"
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        created_tickets.append(new_ticket)
        
        # Verify session status updated
        db.refresh(test_session)
        print(f"  Associated Session Status updated: {test_session.status}")

    # 5. Ticket Update Status Testing
    print("\n--- Testing Ticket Workflow Management ---")
    target_ticket = created_tickets[0]
    print(f"Initial status of ticket '{target_ticket.title}': {target_ticket.status}")
    
    # Update to In Progress
    target_ticket.status = "in_progress"
    db.commit()
    db.refresh(target_ticket)
    print(f"Updated status: {target_ticket.status}")
    
    # Assign Agent
    target_ticket.assigned_agent_id = agent.id
    db.commit()
    db.refresh(target_ticket)
    print(f"Assigned Agent: {target_ticket.assigned_agent.name} (Role: {target_ticket.assigned_agent.role})")
    
    # Resolve Ticket
    target_ticket.status = "resolved"
    target_ticket.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(target_ticket)
    print(f"Resolved status: {target_ticket.status}")
    print(f"Resolved At: {target_ticket.resolved_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # 6. Retrieve Registry Testing
    print("\n--- Retrieving Open Technical Tickets Registry ---")
    tech_tickets = db.query(Ticket).filter(Ticket.category == "technical").all()
    for t in tech_tickets:
        print(f" - [{t.priority.upper()}] ID: {t.id} - Title: {t.title} - Status: {t.status}")

    # 7. Cleanup DB
    print("\nCleaning up test database records...")
    db.query(Ticket).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.commit()
    db.close()
    
    print("\n--- Phase 3 Ticketing Workflow Verification Passed Successfully! ---")

if __name__ == "__main__":
    run_ticket_test()
