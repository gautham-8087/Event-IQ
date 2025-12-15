import requests
import json

# Test the chat API
url = "http://127.0.0.1:5000/api/chat"
payload = {"message": "Hello"}
headers = {"Content-Type": "application/json"}

print("Testing Event IQ chatbot...")
print(f"Sending: {payload['message']}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! AI Response:")
        print(data.get('response', 'No response field'))
    else:
        print(f"\n❌ ERROR:")
        print(response.text)
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
