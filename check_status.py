#!/usr/bin/env python3
"""
Quick diagnostic script to check platform status and data
"""

import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def check_platform():
    print("🔍 Checking Tourism Analytics Platform Status...")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Basic health check
            print("1. Testing API connection...")
            response = await client.get(f"{BASE_URL}/health/")
            if response.status_code == 200:
                print("   ✅ API is responding")
                data = response.json()
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Version: {data.get('version', 'Unknown')}")
            else:
                print(f"   ❌ API error: {response.status_code}")
                return False
            
            # 2. Detailed health check
            print("\n2. Checking database and dependencies...")
            response = await client.get(f"{BASE_URL}/health/detailed")
            if response.status_code == 200:
                data = response.json()
                overall_status = data.get('status', 'unknown')
                print(f"   Overall Status: {overall_status}")
                
                checks = data.get('checks', {})
                for service, status in checks.items():
                    icon = "✅" if status['status'] == 'healthy' else "❌"
                    print(f"   {icon} {service.title()}: {status['status']}")
                    if status['status'] != 'healthy' and 'error' in status:
                        print(f"      Error: {status['error']}")
                
                if overall_status != 'healthy':
                    print("\n❌ Platform has health issues. Check the errors above.")
                    return False
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
            
            # 3. Check for existing data
            print("\n3. Checking for existing data...")
            
            review_count = 0
            tourism_count = 0
            lead_count = 0
            session_count = 0
            
            # Check reviews
            try:
                response = await client.get(f"{BASE_URL}/reviews/", params={"business_id": "aloha_resort_waikiki", "limit": 1})
                if response.status_code == 200:
                    reviews = response.json()
                    review_count = len(reviews)
                    print(f"   📝 Reviews: {review_count} found")
                else:
                    print(f"   📝 Reviews: Error {response.status_code}")
                    if response.status_code == 500:
                        print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   📝 Reviews: Exception {e}")
            
            # Check tourism data
            try:
                response = await client.get(f"{BASE_URL}/forecasting/data", params={"business_id": "aloha_resort_waikiki", "limit": 1})
                if response.status_code == 200:
                    data = response.json()
                    tourism_count = len(data.get('data', []))
                    print(f"   📊 Tourism Data: {tourism_count} records found")
                else:
                    print(f"   📊 Tourism Data: Error {response.status_code}")
                    if response.status_code == 500:
                        print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   📊 Tourism Data: Exception {e}")
            
            # Check leads
            try:
                response = await client.get(f"{BASE_URL}/leads/", params={"business_id": "aloha_resort_waikiki", "limit": 1})
                if response.status_code == 200:
                    data = response.json()
                    lead_count = len(data.get('leads', []))
                    print(f"   👥 Leads: {lead_count} found")
                else:
                    print(f"   👥 Leads: Error {response.status_code}")
                    if response.status_code == 500:
                        print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   👥 Leads: Exception {e}")
            
            # Check chat sessions
            try:
                response = await client.get(f"{BASE_URL}/chat/analytics", params={"business_id": "aloha_resort_waikiki"})
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        session_count = data.get('analytics', {}).get('total_sessions', 0)
                        print(f"   💬 Chat Sessions: {session_count} found")
                    else:
                        print(f"   💬 Chat Sessions: 0 found")
                else:
                    print(f"   💬 Chat Sessions: Error {response.status_code}")
                    if response.status_code == 500:
                        print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   💬 Chat Sessions: Exception {e}")
            
            print("\n4. Platform Status Summary:")
            if review_count == 0 and tourism_count == 0 and lead_count == 0:
                print("   📭 No data found - You need to run the seeding script")
                print("   🚀 Run: python seed_data.py")
                return "no_data"
            elif review_count > 0 or tourism_count > 0 or lead_count > 0:
                print("   ✅ Data found - Platform ready for demo")
                print("   🎮 Run: python demo.py")
                return "has_data"
            
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")
            print("   Make sure the platform is running:")
            print("   docker-compose up")
            return False

async def main():
    status = await check_platform()
    
    if status == "no_data":
        print("\n" + "="*50)
        print("🎯 NEXT STEPS:")
        print("1. Your platform is running but has no data")
        print("2. Run the seeding script: python seed_data.py")
        print("3. Then run the demo: python demo.py")
    elif status == "has_data":
        print("\n" + "="*50)
        print("🎉 PLATFORM READY!")
        print("1. Your platform has data and is working")
        print("2. Run the demo: python demo.py")
        print("3. Or explore: http://localhost:8000/docs")
    elif status == False:
        print("\n" + "="*50)
        print("🚨 PLATFORM ISSUES:")
        print("1. Make sure Docker is running: docker-compose up")
        print("2. Check for error messages above")
        print("3. Try: docker-compose down && docker-compose up --build")

if __name__ == "__main__":
    asyncio.run(main())