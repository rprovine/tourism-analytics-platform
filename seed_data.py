#!/usr/bin/env python3
"""
Tourism Analytics Platform - Hawaiian Hotels Demo Data Seeder
Populates the platform with realistic data for demonstration purposes.
"""

import asyncio
import httpx
import random
from datetime import datetime, timedelta, date
from typing import List, Dict
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Hawaiian hotel data
HAWAIIAN_HOTELS = [
    {
        "business_id": "aloha_resort_waikiki",
        "name": "Aloha Resort Waikiki",
        "location": "Honolulu, Hawaii",
        "category": "resort"
    },
    {
        "business_id": "maui_beach_hotel",
        "name": "Maui Beach Hotel & Spa",
        "location": "Maui, Hawaii", 
        "category": "hotel"
    },
    {
        "business_id": "kona_village_resort",
        "name": "Kona Village Resort",
        "location": "Big Island, Hawaii",
        "category": "resort"
    },
    {
        "business_id": "halekulani_luxury",
        "name": "Halekulani Luxury Hotel",
        "location": "Honolulu, Hawaii",
        "category": "luxury"
    },
    {
        "business_id": "napali_coast_inn",
        "name": "Napali Coast Inn",
        "location": "Kauai, Hawaii",
        "category": "boutique"
    }
]

# Sample review templates
REVIEW_TEMPLATES = [
    # Positive reviews
    {
        "text": "Amazing stay at {}! The ocean views were breathtaking and the staff was incredibly friendly. The luau dinner was a highlight of our trip. Highly recommend the sunset cruise they arranged for us.",
        "rating": 5.0,
        "sentiment": "positive"
    },
    {
        "text": "Wonderful experience at {}. Beautiful beachfront location with pristine white sand. The Hawaiian cultural activities were authentic and engaging. Our room was spacious and well-appointed.",
        "rating": 4.8,
        "sentiment": "positive"
    },
    {
        "text": "Fantastic resort! {} exceeded all our expectations. The infinity pool overlooking the Pacific was incredible. Staff went above and beyond to make our honeymoon special.",
        "rating": 4.9,
        "sentiment": "positive"
    },
    {
        "text": "Great location at {} with easy access to Waikiki Beach. The traditional Hawaiian breakfast was delicious. Kids loved the snorkeling activities and turtle watching tours.",
        "rating": 4.5,
        "sentiment": "positive"
    },
    
    # Mixed reviews
    {
        "text": "Nice stay at {} overall. The location is perfect and views are stunning. However, the restaurant was quite expensive and service could be faster. Room was clean and comfortable.",
        "rating": 3.8,
        "sentiment": "neutral"
    },
    {
        "text": "Decent hotel at {}. Good value for money in Hawaii. The pool area gets crowded but the beach access is convenient. WiFi was spotty in some areas.",
        "rating": 3.5,
        "sentiment": "neutral"
    },
    {
        "text": "{} has a great location but needs some updates. The elevator was slow and our room felt dated. However, the mai tais at the tiki bar were excellent!",
        "rating": 3.2,
        "sentiment": "neutral"
    },
    
    # Negative reviews
    {
        "text": "Disappointed with our stay at {}. The room was smaller than expected and quite noisy due to construction nearby. The advertised beach access was limited during high tide.",
        "rating": 2.5,
        "sentiment": "negative"
    },
    {
        "text": "Overpriced for what you get at {}. The air conditioning barely worked and housekeeping missed our room twice. Beautiful location but poor service quality.",
        "rating": 2.2,
        "sentiment": "negative"
    },
    {
        "text": "Would not recommend {}. Check-in took over an hour and our reservation was somehow lost. The promised ocean view room faced a parking lot instead.",
        "rating": 1.8,
        "sentiment": "negative"
    }
]

# Sample reviewer names
REVIEWER_NAMES = [
    "Sarah Johnson", "Mike Chen", "Emily Rodriguez", "David Kim", "Jessica Brown",
    "Alex Thompson", "Maria Garcia", "Chris Wilson", "Amanda Davis", "Ryan Martinez",
    "Lisa Anderson", "Kevin Lee", "Nicole Taylor", "Brandon White", "Ashley Moore",
    "Tyler Jackson", "Samantha Miller", "Jordan Davis", "Rachel Green", "Austin Clark"
]

# Sample chat scenarios
CHAT_SCENARIOS = [
    {
        "messages": [
            {"user": "Hi, I'm looking for a hotel in Hawaii for my family vacation", "intent": "information"},
            {"user": "We need 2 rooms for 4 adults and 2 children", "intent": "booking"},
            {"user": "What dates do you have available in July?", "intent": "booking"},
            {"user": "Perfect! Can we book July 15-22?", "intent": "booking"}
        ],
        "language": "en"
    },
    {
        "messages": [
            {"user": "Aloha! What activities do you recommend for kids?", "intent": "recommendation"},
            {"user": "My kids are 8 and 12 years old", "intent": "information"},
            {"user": "Do you have snorkeling tours?", "intent": "information"},
            {"user": "How much does the sunset dinner cruise cost?", "intent": "pricing"}
        ],
        "language": "en"
    },
    {
        "messages": [
            {"user": "I need to cancel my reservation", "intent": "cancellation"},
            {"user": "The booking is under Johnson for next week", "intent": "cancellation"},
            {"user": "What is your cancellation policy?", "intent": "information"}
        ],
        "language": "en"
    },
    {
        "messages": [
            {"user": "Hola, ¿tienen habitaciones disponibles?", "intent": "booking"},
            {"user": "Para dos personas, del 20 al 25 de agosto", "intent": "booking"},
            {"user": "¿Cuánto cuesta por noche?", "intent": "pricing"}
        ],
        "language": "es"
    }
]

# Sample lead data
LEAD_TEMPLATES = [
    {
        "first_name": "Jennifer",
        "last_name": "Smith",
        "email": "jennifer.smith@email.com",
        "phone": "+1-555-0123",
        "lead_source": "website",
        "travel_dates": "2024-08-15 to 2024-08-22",
        "destination": "Maui",
        "party_size": 2,
        "budget_range": "$3000-5000",
        "service_interests": ["accommodation", "dining", "activities"],
        "interest_level": "hot"
    },
    {
        "first_name": "Michael",
        "last_name": "Chang",
        "email": "m.chang@email.com", 
        "phone": "+1-555-0456",
        "lead_source": "social_media",
        "travel_dates": "2024-07-10 to 2024-07-17",
        "destination": "Honolulu",
        "party_size": 4,
        "budget_range": "$5000-8000",
        "service_interests": ["family_activities", "accommodation", "transportation"],
        "interest_level": "warm"
    },
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.j@email.com",
        "phone": "+1-555-0789",
        "lead_source": "chat",
        "travel_dates": "2024-09-05 to 2024-09-12",
        "destination": "Big Island",
        "party_size": 2,
        "budget_range": "$4000-6000",
        "service_interests": ["honeymoon_package", "spa", "dining"],
        "interest_level": "hot"
    }
]

class DemoDataSeeder:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()
    
    async def seed_reviews(self, business_id: str, hotel_name: str, num_reviews: int = 25):
        """Generate and create sample reviews for a hotel"""
        print(f"Seeding {num_reviews} reviews for {hotel_name}...")
        
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_reviews):
            # Pick random review template
            template = random.choice(REVIEW_TEMPLATES)
            reviewer_name = random.choice(REVIEWER_NAMES)
            
            # Create review date (more recent reviews more likely)
            days_ago = random.choices(
                range(0, 90),
                weights=[3 if d < 30 else 2 if d < 60 else 1 for d in range(90)],
                k=1
            )[0]
            
            review_date = start_date + timedelta(days=days_ago)
            
            # Add some rating variation
            rating = template["rating"] + random.uniform(-0.3, 0.3)
            rating = max(1.0, min(5.0, rating))
            
            review_data = {
                "business_id": business_id,
                "reviewer_name": reviewer_name,
                "reviewer_email": f"{reviewer_name.lower().replace(' ', '.')}@email.com",
                "rating": round(rating, 1),
                "review_text": template["text"].format(hotel_name),
                "language": "en",
                "source": random.choice(["google", "tripadvisor", "booking.com", "expedia"])
            }
            
            try:
                response = await self.client.post(f"{BASE_URL}/reviews/", json=review_data)
                if response.status_code == 200:
                    print(f"  ✓ Created review {i+1}/{num_reviews}")
                else:
                    print(f"  ✗ Failed to create review {i+1}: {response.status_code}")
                    print(f"    Response: {response.text}")
            except Exception as e:
                print(f"  ✗ Error creating review {i+1}: {e}")
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.1)
    
    async def seed_tourism_data(self, business_id: str, hotel_name: str, days: int = 180):
        """Generate historical tourism data for forecasting"""
        print(f"Seeding {days} days of tourism data for {hotel_name}...")
        
        start_date = datetime.now().date() - timedelta(days=days)
        tourism_data = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # Simulate seasonal patterns
            month = current_date.month
            is_peak_season = month in [6, 7, 8, 12]  # Summer and December
            is_weekend = current_date.weekday() >= 5
            is_holiday = self._is_holiday(current_date)
            
            # Base visitor count with seasonal variation
            base_visitors = 120 if is_peak_season else 80
            weekend_boost = 1.3 if is_weekend else 1.0
            holiday_boost = 1.5 if is_holiday else 1.0
            
            # Add random variation
            visitor_count = int(base_visitors * weekend_boost * holiday_boost * random.uniform(0.7, 1.3))
            
            # Calculate other metrics
            avg_room_rate = random.uniform(250, 450) if is_peak_season else random.uniform(180, 320)
            occupancy = min(0.95, visitor_count / 150)
            revenue = visitor_count * avg_room_rate * random.uniform(0.8, 1.2)
            bookings = int(visitor_count * random.uniform(0.6, 0.9))
            cancellations = int(bookings * random.uniform(0.05, 0.15))
            
            tourism_data.append({
                "business_id": business_id,
                "date": current_date.isoformat(),
                "visitor_count": visitor_count,
                "revenue": round(revenue, 2),
                "bookings": bookings,
                "cancellations": cancellations,
                "occupancy_rate": round(occupancy, 3),
                "average_stay_duration": round(random.uniform(3.2, 7.8), 1),
                "source_market": random.choice(["domestic", "international", "inter_island"]),
                "weather_condition": random.choice(["sunny", "partly_cloudy", "cloudy", "rainy"]),
                "temperature": round(random.uniform(72, 86), 1),
                "is_holiday": is_holiday,
                "is_weekend": is_weekend,
                "special_event": self._get_special_event(current_date),
                "marketing_spend": round(random.uniform(500, 2000), 2)
            })
        
        # Bulk insert tourism data
        try:
            response = await self.client.post(f"{BASE_URL}/forecasting/data/bulk", json=tourism_data)
            if response.status_code == 200:
                print(f"  ✓ Created {len(tourism_data)} tourism data records")
            else:
                print(f"  ✗ Failed to create tourism data: {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating tourism data: {e}")
    
    async def seed_chat_sessions(self, business_id: str, num_sessions: int = 15):
        """Generate sample chat sessions"""
        print(f"Seeding {num_sessions} chat sessions...")
        
        for i in range(num_sessions):
            scenario = random.choice(CHAT_SCENARIOS)
            
            # Create chat session
            session_data = {
                "business_id": business_id,
                "language": scenario["language"],
                "user_location": random.choice(["California", "New York", "Texas", "Florida", "Washington"])
            }
            
            try:
                response = await self.client.post(f"{BASE_URL}/chat/session", json=session_data)
                if response.status_code != 200:
                    print(f"  ✗ Failed to create chat session {i+1}")
                    continue
                
                session_id = response.json()["session_id"]
                print(f"  ✓ Created chat session {i+1}/{num_sessions}")
                
                # Send messages in the scenario
                for message_data in scenario["messages"]:
                    message_payload = {
                        "session_id": session_id,
                        "message": message_data["user"],
                        "business_id": business_id
                    }
                    
                    msg_response = await self.client.post(f"{BASE_URL}/chat/message", json=message_payload)
                    await asyncio.sleep(0.5)  # Simulate conversation delay
                
                # Add random feedback
                if random.random() < 0.7:  # 70% chance of feedback
                    feedback_data = {
                        "session_id": session_id,
                        "rating": random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0],
                        "feedback_text": random.choice([
                            "Very helpful!", "Quick responses", "Understood my needs well",
                            "Could be more detailed", "Good overall experience"
                        ]) if random.random() < 0.5 else None
                    }
                    
                    await self.client.post(f"{BASE_URL}/chat/feedback", json=feedback_data)
                
            except Exception as e:
                print(f"  ✗ Error creating chat session {i+1}: {e}")
            
            await asyncio.sleep(0.2)
    
    async def seed_leads(self, business_id: str, num_leads: int = 12):
        """Generate sample leads"""
        print(f"Seeding {num_leads} leads...")
        
        for i in range(num_leads):
            lead_template = random.choice(LEAD_TEMPLATES)
            
            # Modify template data to create unique leads
            lead_data = lead_template.copy()
            lead_data["business_id"] = business_id
            lead_data["email"] = f"lead{i}_{lead_data['email']}"
            lead_data["lead_score"] = random.randint(20, 95)
            lead_data["notes"] = f"Interested in {random.choice(['luxury', 'family-friendly', 'romantic', 'adventure'])} package"
            
            # Randomize some fields
            if random.random() < 0.3:
                lead_data["lead_status"] = random.choice(["contacted", "qualified", "converted"])
            
            try:
                response = await self.client.post(f"{BASE_URL}/leads/", json=lead_data, params={"sync_to_hubspot": False})
                if response.status_code == 200:
                    print(f"  ✓ Created lead {i+1}/{num_leads}")
                    
                    # Add some activities for this lead
                    lead_id = response.json()["lead_id"]
                    await self._add_lead_activities(lead_id)
                    
                    # Convert some leads
                    if random.random() < 0.2:  # 20% conversion rate
                        conversion_value = random.uniform(2000, 8000)
                        await self.client.post(
                            f"{BASE_URL}/leads/{lead_id}/convert",
                            params={"conversion_value": conversion_value, "create_deal": False}
                        )
                        print(f"    ✓ Converted lead {i+1}")
                        
                else:
                    print(f"  ✗ Failed to create lead {i+1}: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Error creating lead {i+1}: {e}")
            
            await asyncio.sleep(0.1)
    
    async def _add_lead_activities(self, lead_id: int):
        """Add sample activities to a lead"""
        activities = [
            {
                "activity_type": "email",
                "subject": "Welcome to Hawaiian Paradise",
                "description": "Sent welcome email with travel guide",
                "activity_date": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
                "outcome": "sent"
            },
            {
                "activity_type": "call",
                "subject": "Follow-up call",
                "description": "Discussed travel preferences and budget",
                "activity_date": (datetime.now() - timedelta(days=random.randint(0, 3))).isoformat(),
                "duration_minutes": random.randint(10, 30),
                "outcome": random.choice(["completed", "voicemail", "no_answer"])
            }
        ]
        
        for activity in activities:
            if random.random() < 0.6:  # 60% chance of each activity
                try:
                    await self.client.post(
                        f"{BASE_URL}/leads/{lead_id}/activities",
                        json=activity,
                        params={"sync_to_hubspot": False}
                    )
                except:
                    pass  # Ignore activity creation errors
    
    async def train_models(self, business_id: str):
        """Train the forecasting models with the seeded data"""
        print(f"Training forecasting models for {business_id}...")
        
        try:
            response = await self.client.post(f"{BASE_URL}/forecasting/train", params={"business_id": business_id})
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Models trained successfully")
                print(f"    Best model: {result.get('best_model', 'unknown')}")
            else:
                print(f"  ✗ Failed to train models: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error training models: {e}")
    
    def _is_holiday(self, date_obj: date) -> bool:
        """Check if date is a holiday"""
        holidays = [
            (1, 1),   # New Year
            (7, 4),   # Independence Day
            (11, 11), # Veterans Day
            (12, 25), # Christmas
        ]
        return (date_obj.month, date_obj.day) in holidays
    
    def _get_special_event(self, date_obj: date) -> str:
        """Get special event for date"""
        month, day = date_obj.month, date_obj.day
        
        events = {
            (3, 26): "Prince Kuhio Day",
            (6, 11): "King Kamehameha Day", 
            (8, 21): "Statehood Day",
            (5, 1): "Lei Day",
            (9, 23): "Aloha Festival"
        }
        
        return events.get((month, day), None)

async def main():
    """Main seeding function"""
    seeder = DemoDataSeeder()
    
    try:
        print("🌺 Starting Hawaiian Hotels Demo Data Seeding...")
        print("=" * 60)
        
        # Seed data for each hotel
        for i, hotel in enumerate(HAWAIIAN_HOTELS, 1):
            print(f"\n🏨 Seeding data for {hotel['name']} ({i}/{len(HAWAIIAN_HOTELS)})")
            print("-" * 40)
            
            business_id = hotel['business_id']
            hotel_name = hotel['name']
            
            # Seed different amounts of data based on hotel type
            if hotel['category'] == 'luxury':
                review_count = 35
                lead_count = 15
                chat_count = 20
            elif hotel['category'] == 'resort':
                review_count = 45
                lead_count = 20
                chat_count = 25
            else:
                review_count = 25
                lead_count = 10
                chat_count = 15
            
            # Seed all data types
            await seeder.seed_reviews(business_id, hotel_name, review_count)
            await seeder.seed_tourism_data(business_id, hotel_name, 180)
            await seeder.seed_chat_sessions(business_id, chat_count)
            await seeder.seed_leads(business_id, lead_count)
            
            # Train models for this hotel
            await seeder.train_models(business_id)
            
            print(f"✅ Completed seeding for {hotel_name}")
        
        print("\n" + "=" * 60)
        print("🎉 Demo data seeding completed successfully!")
        print("\nYou can now explore:")
        print("• Sentiment Analytics: http://localhost:8000/docs#/reviews")
        print("• Demand Forecasting: http://localhost:8000/docs#/forecasting") 
        print("• Chat Analytics: http://localhost:8000/docs#/chat")
        print("• Lead Management: http://localhost:8000/docs#/leads")
        print("• Business Dashboards: http://localhost:8000/docs#/dashboard")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
    finally:
        await seeder.close()

if __name__ == "__main__":
    asyncio.run(main())