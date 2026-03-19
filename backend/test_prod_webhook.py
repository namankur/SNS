import httpx
import asyncio

async def test_prod_webhook():
    # The production backend URL
    url = "https://sns-production-a328.up.railway.app/webhook/sms"
    
    # Mock TextBee payload
    # Sending from Namankur's registered phone (6360168288)
    payload = {
        "smsId": "test-123",
        "message": "papa",
        "sender": "6360168288",
        "webhookEvent": "MESSAGE_RECEIVED"
    }
    
    print(f"Sending mock webhook to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_prod_webhook())
