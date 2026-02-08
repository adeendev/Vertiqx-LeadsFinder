import sqlite3
import os

DB_PATH = "leads.db"

def check_db():
    print(f"Checking database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database file NOT found!")
        return
        
    print("✅ Database file exists.")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tables found: {tables}")
        
        if not any('lead' in t[0] for t in tables):
            print("❌ 'lead' table missing!")
        else:
            print("✅ 'lead' table exists.")
            
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM lead")
            count = cursor.fetchone()[0]
            print(f"📈 Total leads in DB: {count}")
            
            if count > 0:
                cursor.execute("SELECT business_name, tier, final_priority FROM lead LIMIT 3")
                print("📝 Sample Data:")
                for row in cursor.fetchall():
                    print(row)
                    
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_db()
