import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"

headers = {
    'Authorization': f'Bearer {OLLAMA_API_KEY}',
    'Content-Type': 'application/json'
}

payload = {
    "model": "gpt-oss:120b",
    "messages": [
        {
            "role": "user",
            "content": "Say hello as coco assistant in one sentence"
        }
    ],
    "stream": False
}

response = requests.post(OLLAMA_CLOUD_URL, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"SUCCESS: Cloud API Working!")
    print(f"Response: {result['message']['content']}")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)
