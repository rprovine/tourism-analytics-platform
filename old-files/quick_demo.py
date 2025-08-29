#!/usr/bin/env python3
"""
Quick demo setup - creates minimal data for immediate testing
"""

import asyncio
import httpx
import random
from datetime import datetime, timedelta, date

BASE_URL = "http://localhost:8000/api/v1"
BUSINESS_ID = "aloha_resort_waikiki"

async def quick_setup():
    print("🌺 Setting up quick demo data for Aloha Resort Waikiki...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Create 10 quick reviews
        print("📝 Creating sample reviews...")
        reviews = [
            {"rating": 5.0, "text": "Amazing stay! The ocean views were breathtaking and staff was incredibly friendly.", "sentiment": "positive"},
            {"rating": 4.8, "text": "Beautiful beachfront location with pristine white sand. Great Hawaiian cultural activities.", "sentiment": "positive"},
            {"rating": 4.5, "text": "Fantastic resort! Exceeded all expectations. The infinity pool was incredible.", "sentiment": "positive"},
            {"rating": 4.2, "text": "Great location with easy access to Waikiki Beach. Kids loved the snorkeling.", "sentiment": "positive"},
            {"rating": 3.8, "text": "Nice stay overall. Perfect location but restaurant was expensive. Room was clean.", "sentiment": "neutral"},
            {"rating": 3.5, "text": "Decent hotel. Good value for Hawaii. Pool gets crowded but beach access is convenient.", "sentiment": "neutral"},
            {"rating": 3.0, "text": "Hotel has great location but needs updates. Elevator was slow but mai tais were good!", "sentiment": "neutral"},
            {"rating": 2.8, "text": "Disappointed with our stay. Room smaller than expected and noisy due to construction.", "sentiment": "negative"},
            {"rating": 2.5, "text": "Overpriced for what you get. Air conditioning barely worked and housekeeping missed our room.", "sentiment": "negative"},
            {"rating": 2.0, "text": "Would not recommend. Check-in took forever and ocean view room faced parking lot.", "sentiment": "negative"},
        ]
        
        names = ["Sarah J.", "Mike C.", "Emily R.", "David K.", "Jessica B.", "Alex T.", "Maria G.", "Chris W.", "Amanda D.", "Ryan M."]
        
        for i, review in enumerate(reviews):
            review_data = {
                "business_id": BUSINESS_ID,
                "reviewer_name": names[i],
                "rating": review["rating"],
                "review_text": review["text"],
                "language": "en",
                "source": random.choice(["google", "tripadvisor", "booking.com"])
            }
            
            try:
                response = await client.post(f"{BASE_URL}/reviews/", json=review_data)
                if response.status_code == 200:
                    print(f"  ✓ Review {i+1}/10 created")
                else:
                    print(f"  ✗ Review {i+1} failed: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Review {i+1} error: {e}")
        
        # 2. Create 30 days of tourism data
        print("\n📊 Creating tourism data...")
        start_date = datetime.now().date() - timedelta(days=30)
        
        tourism_batch = []
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            
            # Simulate realistic data
            base_visitors = 100
            is_weekend = current_date.weekday() >= 5
            weekend_boost = 1.4 if is_weekend else 1.0
            visitor_count = int(base_visitors * weekend_boost * random.uniform(0.8, 1.2))
            
            tourism_batch.append({
                "business_id": BUSINESS_ID,
                "date": current_date.isoformat(),
                "visitor_count": visitor_count,
                "revenue": round(visitor_count * random.uniform(280, 420), 2),
                "bookings": int(visitor_count * random.uniform(0.6, 0.8)),
                "cancellations": int(visitor_count * random.uniform(0.05, 0.12)),
                "occupancy_rate": round(min(0.95, visitor_count / 120), 3),
                "average_stay_duration": round(random.uniform(3.5, 6.2), 1),
                "source_market": random.choice(["domestic", "international"]),
                "weather_condition": random.choice(["sunny", "partly_cloudy", "cloudy"]),
                "temperature": round(random.uniform(75, 84), 1),
                "is_holiday": False,
                "is_weekend": is_weekend,
                "special_event": None,
                "marketing_spend": round(random.uniform(800, 1500), 2)
            })
        
        try:
            response = await client.post(f"{BASE_URL}/forecasting/data/bulk", json=tourism_batch)
            if response.status_code == 200:
                print(f"  ✓ Created 30 days of tourism data")
            else:
                print(f"  ✗ Tourism data failed: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Tourism data error: {e}")
        
        # 3. Create a few leads
        print("\n👥 Creating sample leads...")
        leads = [
            {
                "first_name": "Jennifer", "last_name": "Smith", "email": "jennifer.s@email.com",
                "travel_dates": "2024-08-15 to 2024-08-22", "party_size": 2, "budget_range": "$4000-6000",
                "lead_source": "website", "interest_level": "hot"
            },
            {
                "first_name": "Michael", "last_name": "Chen", "email": "m.chen@email.com", 
                "travel_dates": "2024-07-20 to 2024-07-27", "party_size": 4, "budget_range": "$6000-8000",
                "lead_source": "social_media", "interest_level": "warm"
            },
            {
                "first_name": "Sarah", "last_name": "Johnson", "email": "s.johnson@email.com",
                "travel_dates": "2024-09-10 to 2024-09-17", "party_size": 2, "budget_range": "$5000-7000", 
                "lead_source": "referral", "interest_level": "hot"
            }
        ]
        
        for i, lead in enumerate(leads):
            lead["business_id"] = BUSINESS_ID
            lead["lead_score"] = random.randint(60, 95)
            lead["destination"] = "Honolulu"
            lead["service_interests"] = ["accommodation", "activities"]
            
            try:
                response = await client.post(f"{BASE_URL}/leads/", json=lead, params={"sync_to_hubspot": False})
                if response.status_code == 200:
                    print(f"  ✓ Lead {i+1}/3 created")
                else:
                    print(f"  ✗ Lead {i+1} failed: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Lead {i+1} error: {e}")
        
        # 4. Create a chat session
        print("\n💬 Creating sample chat session...")
        try:
            session_response = await client.post(f"{BASE_URL}/chat/session", json={
                "business_id": BUSINESS_ID,
                "language": "en"
            })
            
            if session_response.status_code == 200:
                session_id = session_response.json()["session_id"]
                print(f"  ✓ Chat session created")
                
                # Send a few messages
                messages = [
                    "Hi! I'm interested in booking a room for my honeymoon",
                    "We're looking for something romantic with ocean views",
                    "What's included in your honeymoon package?"
                ]
                
                for msg in messages:
                    await client.post(f"{BASE_URL}/chat/message", json={
                        "session_id": session_id,
                        "message": msg,
                        "business_id": BUSINESS_ID
                    })
                    await asyncio.sleep(0.5)
                
                print(f"  ✓ Sample conversation created")
        except Exception as e:
            print(f"  ✗ Chat session error: {e}")
        
        # 5. Train forecasting model
        print("\n🤖 Training forecasting model...")
        try:
            response = await client.post(f"{BASE_URL}/forecasting/train", params={"business_id": BUSINESS_ID})
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Model trained successfully")
            else:
                print(f"  ✗ Training failed: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Training error: {e}")
        
        print("\n🎉 Quick demo setup complete!")
        print("You can now:")
        print("• Visit: http://localhost:8000/docs")
        print("• Run: python demo.py")
        print("• Try the API endpoints with real data")

if __name__ == "__main__":
    asyncio.run(quick_setup())