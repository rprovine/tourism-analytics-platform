"""
In-memory demo database for deployment without PostgreSQL
Contains all the seed data from the original platform
"""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional

class DemoDatabase:
    def __init__(self):
        self.hotels = []
        self.tourism_data = []
        self.reviews = []
        self.chat_sessions = []
        self.chat_messages = []
        self.leads = []
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with Hawaiian hotel demo data"""
        # Hotels
        self.hotels = [
            {
                "id": 1,
                "name": "Aloha Beach Resort",
                "location": "Waikiki, Honolulu",
                "description": "Beachfront resort in the heart of Waikiki with stunning ocean views",
                "rooms": 350,
                "amenities": ["Beach Access", "Pool", "Spa", "Restaurant", "Fitness Center"],
                "contact_email": "info@alohabeach.com",
                "contact_phone": "+1-808-555-0101"
            },
            {
                "id": 2,
                "name": "Maui Paradise Hotel",
                "location": "Wailea, Maui",
                "description": "Luxury resort with championship golf course and world-class spa",
                "rooms": 280,
                "amenities": ["Golf Course", "Spa", "Multiple Restaurants", "Private Beach", "Tennis Court"],
                "contact_email": "reservations@mauiparadise.com", 
                "contact_phone": "+1-808-555-0102"
            },
            {
                "id": 3,
                "name": "Big Island Retreat",
                "location": "Kona, Big Island",
                "description": "Eco-friendly resort with volcano views and cultural experiences",
                "rooms": 150,
                "amenities": ["Volcano Tours", "Cultural Center", "Organic Restaurant", "Hiking Trails"],
                "contact_email": "welcome@bigislandretreat.com",
                "contact_phone": "+1-808-555-0103"
            },
            {
                "id": 4,
                "name": "Kauai Garden Resort",
                "location": "Poipu, Kauai",
                "description": "Tropical paradise surrounded by lush gardens and pristine beaches",
                "rooms": 200,
                "amenities": ["Botanical Gardens", "Snorkeling", "Spa", "Multiple Pools", "Kids Club"],
                "contact_email": "info@kauaigarden.com",
                "contact_phone": "+1-808-555-0104"
            },
            {
                "id": 5,
                "name": "Lanai Luxury Lodge",
                "location": "Lanai City, Lanai",
                "description": "Exclusive boutique resort offering ultimate privacy and luxury",
                "rooms": 75,
                "amenities": ["Private Butler", "Gourmet Restaurant", "Exclusive Beach", "Helicopter Tours"],
                "contact_email": "concierge@lanailuxury.com",
                "contact_phone": "+1-808-555-0105"
            }
        ]
        
        # Tourism Data (last 90 days)
        base_date = datetime.now() - timedelta(days=90)
        for i in range(90):
            date = base_date + timedelta(days=i)
            for hotel in self.hotels:
                # Simulate seasonal patterns and weekend effects
                day_of_week = date.weekday()
                is_weekend = day_of_week >= 5
                seasonal_factor = 1.0 + 0.3 * (i / 90)  # Increasing over time
                weekend_factor = 1.2 if is_weekend else 1.0
                
                base_occupancy = 65 + random.randint(-15, 25)
                occupancy = min(95, max(30, base_occupancy * seasonal_factor * weekend_factor))
                
                revenue = hotel["rooms"] * occupancy * random.uniform(180, 350) / 100
                bookings = int(occupancy * hotel["rooms"] / 100 * random.uniform(0.8, 1.2))
                
                self.tourism_data.append({
                    "id": len(self.tourism_data) + 1,
                    "date": date.date(),
                    "hotel_id": hotel["id"],
                    "hotel_name": hotel["name"],
                    "location": hotel["location"],
                    "visitors": bookings,
                    "revenue": round(revenue, 2),
                    "occupancy_rate": round(occupancy, 1),
                    "avg_stay": random.uniform(3.5, 7.2),
                    "satisfaction_score": random.uniform(4.0, 4.9),
                    "weather_condition": random.choice(["sunny", "partly_cloudy", "rainy"]),
                    "season": self._get_season(date),
                    "bookings": bookings
                })
        
        # Reviews
        review_texts = [
            ("Amazing beachfront location! Perfect for families.", 5, "positive"),
            ("Great service, but rooms could be updated.", 4, "neutral"),
            ("Luxury at its finest. The spa was incredible!", 5, "positive"),
            ("Expensive but worth it for special occasions.", 3, "neutral"),
            ("Peaceful retreat with stunning volcano views.", 4, "positive"),
            ("Hidden gem! Best snorkeling right from the beach.", 5, "positive"),
            ("Ultimate luxury experience. Every detail perfect.", 5, "positive"),
            ("Staff was friendly and helpful throughout our stay.", 4, "positive"),
            ("Room was clean but the AC was too loud.", 3, "neutral"),
            ("Breakfast buffet had great variety and quality.", 4, "positive"),
            ("Pool area gets crowded during peak hours.", 3, "neutral"),
            ("The sunset views from our balcony were breathtaking!", 5, "positive"),
            ("WiFi connection was spotty in some areas.", 2, "negative"),
            ("Housekeeping did an excellent job every day.", 5, "positive"),
            ("Restaurant prices are quite high for the portion sizes.", 2, "negative"),
            ("Kids loved the beach activities and games.", 4, "positive"),
            ("Spa treatments were relaxing and professionally done.", 5, "positive"),
            ("Check-in process was smooth and efficient.", 4, "positive"),
            ("Some facilities need maintenance and updating.", 2, "negative"),
            ("Overall a wonderful vacation experience!", 5, "positive")
        ]
        
        for i, (text, rating, sentiment) in enumerate(review_texts):
            hotel_id = (i % len(self.hotels)) + 1
            self.reviews.append({
                "id": i + 1,
                "hotel_id": hotel_id,
                "hotel_name": self.hotels[hotel_id - 1]["name"],
                "rating": rating,
                "review_text": text,
                "sentiment": sentiment,
                "confidence": random.uniform(0.7, 0.95),
                "date": (datetime.now() - timedelta(days=random.randint(1, 30))).date(),
                "guest_name": f"Guest {i + 1}",
                "verified": True
            })
        
        # Chat Sessions and Messages
        for i in range(10):
            session_id = f"demo_session_{i + 1}"
            self.chat_sessions.append({
                "id": i + 1,
                "session_id": session_id,
                "user_id": f"user_{i + 1}",
                "language": random.choice(["en", "ja", "zh", "es", "pt"]),
                "created_at": datetime.now() - timedelta(days=random.randint(0, 7)),
                "last_activity": datetime.now() - timedelta(hours=random.randint(0, 24))
            })
            
            # Add messages for each session
            conversation = [
                ("Hello! I'm planning a trip to Hawaii.", "user"),
                ("Aloha! Welcome! I'd be happy to help you plan your Hawaiian vacation. What kind of experience are you looking for?", "bot"),
                ("I want beautiful beaches and good restaurants.", "user"),
                ("Perfect! I recommend Waikiki Beach for iconic Hawaiian beaches, and for dining, try Duke's Waikiki for seafood with ocean views. Would you like specific hotel recommendations too?", "bot"),
                ("Yes, what hotels do you recommend?", "user"),
                ("For beachfront luxury, I suggest Aloha Beach Resort in Waikiki or Maui Paradise Hotel in Wailea. Both offer stunning ocean views and world-class amenities. What's your budget range?", "bot")
            ]
            
            for j, (message, sender) in enumerate(conversation):
                self.chat_messages.append({
                    "id": len(self.chat_messages) + 1,
                    "session_id": session_id,
                    "message": message,
                    "sender": sender,
                    "timestamp": datetime.now() - timedelta(days=random.randint(0, 7), minutes=j * 5),
                    "intent": "travel_planning" if "trip" in message.lower() or "hotel" in message.lower() else "general",
                    "confidence": random.uniform(0.8, 0.95)
                })
        
        # Leads
        lead_data = [
            ("John Smith", "john.smith@email.com", "+1-555-0123", "Family vacation for 4", "high"),
            ("Maria Garcia", "maria.garcia@email.com", "+1-555-0124", "Honeymoon package", "high"),  
            ("David Chen", "david.chen@email.com", "+1-555-0125", "Corporate retreat", "medium"),
            ("Sarah Johnson", "sarah.j@email.com", "+1-555-0126", "Solo travel", "low"),
            ("Mike Wilson", "mike.w@email.com", "+1-555-0127", "Group booking for 8", "high")
        ]
        
        for i, (name, email, phone, notes, priority) in enumerate(lead_data):
            self.leads.append({
                "id": i + 1,
                "name": name,
                "email": email,
                "phone": phone,
                "source": random.choice(["website", "social_media", "referral", "google_ads"]),
                "status": random.choice(["new", "contacted", "qualified", "converted"]),
                "priority": priority,
                "notes": notes,
                "created_at": datetime.now() - timedelta(days=random.randint(0, 14)),
                "last_contact": datetime.now() - timedelta(days=random.randint(0, 7))
            })
    
    def _get_season(self, date):
        """Determine season based on date"""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    # Query methods
    def get_hotels(self):
        return self.hotels
    
    def get_tourism_data(self, days: int = 30):
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return [d for d in self.tourism_data if d["date"] >= cutoff_date]
    
    def get_reviews(self):
        return self.reviews
    
    def get_chat_sessions(self):
        return self.chat_sessions
    
    def get_chat_messages(self, session_id: Optional[str] = None):
        if session_id:
            return [m for m in self.chat_messages if m["session_id"] == session_id]
        return self.chat_messages
    
    def get_leads(self):
        return self.leads
    
    def get_analytics_summary(self):
        """Get summary analytics"""
        recent_data = self.get_tourism_data(30)
        total_revenue = sum(d["revenue"] for d in recent_data)
        avg_occupancy = sum(d["occupancy_rate"] for d in recent_data) / len(recent_data) if recent_data else 0
        total_visitors = sum(d["visitors"] for d in recent_data)
        avg_rating = sum(r["rating"] for r in self.reviews) / len(self.reviews) if self.reviews else 0
        
        return {
            "total_hotels": len(self.hotels),
            "total_revenue_30d": round(total_revenue, 2),
            "avg_occupancy_30d": round(avg_occupancy, 1),
            "total_visitors_30d": total_visitors,
            "total_reviews": len(self.reviews),
            "average_rating": round(avg_rating, 1),
            "total_chat_sessions": len(self.chat_sessions),
            "total_leads": len(self.leads)
        }

# Global demo database instance
demo_db = DemoDatabase()