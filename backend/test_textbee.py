"""
Test script for TextBee SMS Gateway integration.
Run: python test_textbee.py
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID")
TEXTBEE_BASE_URL = os.getenv("TEXTBEE_BASE_URL", "https://api.textbee.dev/api/v1")

print(f"API Key loaded: {bool(TEXTBEE_API_KEY)}")
print(f"Device ID loaded: {bool(TEXTBEE_DEVICE_ID)}")
print(f"Base URL: {TEXTBEE_BASE_URL}")

# Set the phone number you want to send a test SMS to
TARGET_PHONE = "+916360168288"

if not TEXTBEE_API_KEY or not TEXTBEE_DEVICE_ID:
    print("\nError: Missing TextBee credentials.")
    print("1. Sign up at https://textbee.dev (free)")
    print("2. Install the TextBee Android app on a spare phone")
    print("3. Register the device and copy your API Key + Device ID")
    print("4. Add them to your .env file")
    exit(1)

message_body = (
    "Namaste Test ji 🙏\n"
    "Yeh Safe & Sound ka test SMS hai.\n"
    "Agar aapko yeh mila, TextBee integration kaam kar raha hai! ✅"
)

url = f"{TEXTBEE_BASE_URL}/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
headers = {
    "x-api-key": TEXTBEE_API_KEY,
    "Content-Type": "application/json",
}
payload = {
    "recipients": [TARGET_PHONE],
    "message": message_body,
}

print(f"\nSending test SMS to {TARGET_PHONE}...")
print(f"URL: {url}")

try:
    response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code >= 200 and response.status_code < 300:
        print("\nSUCCESS! SMS sent via TextBee.")
    else:
        print(f"\nFAILED. Check your API key, Device ID, and that the TextBee app is running on your phone.")
except httpx.TimeoutException:
    print("\nRequest timed out. Check if TextBee service is reachable.")
except Exception as e:
    print(f"\nError: {e}")
