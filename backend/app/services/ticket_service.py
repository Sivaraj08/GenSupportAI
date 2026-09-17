import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from ..config import settings

class TicketClassifierService:
    def __init__(self):
        # 1. Seed training data representing typical support topics
        self.training_texts = [
            # Technical Category
            "database connection failed with connection pool timeout",
            "cannot reboot postgresql service, access denied error",
            "the backend crashes whenever I upload a pdf manual",
            "server downtime, cluster nodes are down",
            "error loading embeddings, chroma connection failed",
            "network failure, api gateway returns 502",
            "reboot primary cluster node",
            "application throws internal server error on login",
            
            # Billing Category
            "unrecognized transaction on my credit card statement",
            "how do I request a refund for the billing overcharge?",
            "my subscription was cancelled but I was still charged",
            "change payment method to bank wire transfer",
            "where can I download the pdf invoices for last month?",
            "what is the price of the plan after renewal?",
            
            # Sales Category
            "request a demo of the enterprise support assistant",
            "pricing details for team subscription plans",
            "I want to talk to a sales representative about custom volume",
            "what discounts do you offer for non-profits or education?",
            "upgrade my account to the premium plan",
            "enterprise SLA terms and corporate quotes",
            
            # General Category
            "how do I change my profile password?",
            "where are the settings to enable dark mode?",
            "who is the contact person for support inquiries?",
            "terms of service and privacy policy location",
            "hello, I have a quick question about customer support",
            "what is the company address?"
        ]
        
        self.training_labels = [
            "technical", "technical", "technical", "technical", "technical", "technical", "technical", "technical",
            "billing", "billing", "billing", "billing", "billing", "billing",
            "sales", "sales", "sales", "sales", "sales", "sales",
            "general", "general", "general", "general", "general", "general"
        ]
        
        # 2. Build and train the Scikit-learn classification pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', min_df=1)),
            ('clf', MultinomialNB(alpha=1.0))
        ])
        
        print("Training local ML Ticket Category Classifier...")
        self.pipeline.fit(self.training_texts, self.training_labels)
        print("ML Ticket Classifier trained successfully.")

    def predict_category(self, text: str) -> str:
        """
        Uses the trained TF-IDF + Naive Bayes model to predict the ticket category:
        billing, technical, sales, or general.
        """
        if not text or not text.strip():
            return "general"
            
        prediction = self.pipeline.predict([text])
        return str(prediction[0])

    def predict_priority(self, text: str, sentiment: str = "neutral") -> str:
        """
        Heuristic priority classification incorporating text analysis and message sentiment.
        """
        text_lower = text.lower()
        
        # Keywords indicating critical downtime or financial errors
        critical_keywords = ["down", "crashed", "outage", "broken", "hacked", "security breach", "payment failed", "production down", "emergency"]
        high_keywords = ["refund", "billing error", "overcharge", "access denied", "locked out", "urgent", "asap", "not working"]
        
        # Run priority prediction heuristics
        has_critical = any(kw in text_lower for kw in critical_keywords)
        has_high = any(kw in text_lower for kw in high_keywords)
        
        if sentiment == "negative":
            if has_critical:
                return "critical"
            return "high"
        else:
            if has_critical:
                return "high"
            elif has_high:
                return "high"
            elif "pricing" in text_lower or "demo" in text_lower:
                return "medium"
                
        return "low"

ticket_classifier = TicketClassifierService()
