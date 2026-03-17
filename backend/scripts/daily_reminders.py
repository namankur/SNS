import os
from datetime import datetime

# Simulates the cron job script to send daily reminders for those using missed call fallback
def send_daily_reminders():
    print("Running 7 AM Daily Reminders...")
    # Fetch dear ones who haven't installed app and use missed calls
    # Send WhatsApp: "Namaste [Name] ji, Aaj ka good morning missed call dena mat bhuliega"
    print("Sent: Namaste Savitri ji, Aaj ka good morning missed call dena mat bhuliega")

def check_missing_checkins():
    print("Running 10 AM / 2 PM missed check-in alerts...")
    # Follow-ups if missed call not received
    print("Sent: Maa ne aaj abhi check-in nahi kiya to Caller")

def check_upgrade_prompt():
    print("Running 30-day upgrade prompt check...")
    # If 30 days active on missed call:
    print("Sent: Namaste Savitri ji, Aap 30 din se missed call de rahe hain...")

if __name__ == "__main__":
    current_hour = datetime.now().hour
    if current_hour == 7:
        send_daily_reminders()
    elif current_hour in [10, 14]:
        check_missing_checkins()
    
    check_upgrade_prompt()
