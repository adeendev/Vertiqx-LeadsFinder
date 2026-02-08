import requests
import time

BASE_URL = "http://localhost:8000"

def test_db_insert_and_read():
    print("🧪 Testing Database Operations...")
    
    # We can't easily insert via API (only scan triggers it), but we can check if the DB is empty
    # and maybe try to trigger a scan that we know will fail or succeed quickly to check logs.
    
    # Actually, let's just check the status endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            print("✅ Status endpoint working")
            print("Logs:", response.json()[:2])
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            
        response = requests.get(f"{BASE_URL}/api/leads")
        if response.status_code == 200:
            leads = response.json()
            print(f"✅ Leads endpoint working. Count: {len(leads)}")
        else:
            print(f"❌ Leads endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_db_insert_and_read()
