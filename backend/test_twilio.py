import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load local .env just in case, or use defaults
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

print(f"SID Loaded: {bool(TWILIO_ACCOUNT_SID)}")
print(f"Token Loaded: {bool(TWILIO_AUTH_TOKEN)}")
print(f"SMS Number: {TWILIO_SMS_NUMBER}")
print(f"WhatsApp Number: {TWILIO_WHATSAPP_NUMBER}")

# Add the number you are trying to send the invite to here
TARGET_PHONE = "+916360168288"

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    print("Error: Missing Twilio credentials. Check your .env file.")
    exit(1)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

apk_link = "https://awqhrmnfxsdqospuiamm.supabase.co/storage/v1/object/public/releases/app-debug.apk"
message_body = (
    f"Namaste Test ji 🙏\n"
    f"*Rahul* ne aapke liye Safe & Sound setup kiya hai. "
    f"App install karne kr liye is link pe click karein:\n{apk_link}\n\n"
    f"Koi sawaal hai toh yahan reply karein."
)

try:
    from_number = TWILIO_SMS_NUMBER
    to_number = TARGET_PHONE
    
    if TWILIO_WHATSAPP_NUMBER:
        print("Attempting to send via WhatsApp...")
        from_number = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        to_number = f"whatsapp:{TARGET_PHONE}"
    else:
        print("Attempting to send via standard SMS...")

    print(f"Sending from: {from_number}")
    print(f"Sending to: {to_number}")

    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )
    print(f"Success! Message SID: {message.sid}")

except Exception as e:
    print(f"\n--- TWILIO ERROR ---")
    print(str(e))
    print("---------------------\n")
    if "21603" in str(e):
        print("Error 21603: The 'To' phone number is not properly formatted or not verified.")
        print("Make sure you add the country code (e.g. +91) and that the number is verified in Twilio if using a Trial account.")
    elif "63015" in str(e):
        print("Error 63015: The 'To' number has not 'joined' the WhatsApp sandbox.")
        print("Fix: Send 'join <sandbox-word>' to your Twilio WhatsApp number from the target phone first!")
