import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_gmail():
    host = os.getenv("GMAIL_HOST")
    port = int(os.getenv("GMAIL_PORT", 587))
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")

    print(f"\n--- Testing GMAIL ({host}:{port}) ---")
    print(f"User: {user}")
    print(f"Password: {password[:2]}...{password[-2:]} (Length: {len(password)})")

    try:
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(user, password)
        print("✅ GMAIL SUCCESS: Authentication accepted.")
        server.quit()
    except Exception as e:
        print(f"❌ GMAIL FAILED: {e}")

def test_hostinger():
    host = os.getenv("HOSTINGER_HOST")
    port = int(os.getenv("HOSTINGER_PORT", 465))
    user = os.getenv("HOSTINGER_USER")
    password = os.getenv("HOSTINGER_PASS")

    print(f"\n--- Testing HOSTINGER ({host}:{port}) ---")
    print(f"User: {user}")
    print(f"Password: {password[:2]}...{password[-2:]} (Length: {len(password)})")

    try:
        # Hostinger uses SSL usually on 465
        server = smtplib.SMTP_SSL(host, port)
        server.login(user, password)
        print("✅ HOSTINGER SUCCESS: Authentication accepted.")
        server.quit()
    except Exception as e:
        print(f"❌ HOSTINGER FAILED: {e}")

if __name__ == "__main__":
    test_gmail()
    test_hostinger()
