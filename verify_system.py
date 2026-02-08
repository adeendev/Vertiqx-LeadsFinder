import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def check_backend():
    try:
        # Check if we can get leads (should be empty initially)
        response = requests.get(f"{BASE_URL}/api/leads")
        if response.status_code == 200:
            print("✅ Backend is reachable")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def start_scan():
    print("🚀 Starting scan for 'Pizza' in 'Test City'...")
    try:
        response = requests.post(f"{BASE_URL}/api/scan", params={"keyword": "Pizza", "location": "Test City"})
        if response.status_code == 200:
            print("✅ Scan started successfully")
            return True
        else:
            print(f"❌ Scan start failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scan request failed: {e}")
        return False

def check_results():
    print("⏳ Waiting for results (15 seconds)...")
    time.sleep(15)
    
    try:
        response = requests.get(f"{BASE_URL}/api/leads")
        leads = response.json()
        print(f"📊 Found {len(leads)} leads so far")
        
        if len(leads) > 0:
            print("✅ Operation successful! Sample lead:")
            print(leads[0])
        else:
            print("⚠️ No leads found yet. Scraper might still be running or found nothing.")
            
    except Exception as e:
        print(f"❌ Failed to fetch results: {e}")

if __name__ == "__main__":
    if check_backend():
        if start_scan():
            check_results()
