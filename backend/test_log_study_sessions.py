import requests

data = {
    "topic_id": 3,               # change this ID if your topic is different
    "duration_minutes": 60,
    "completed": True,
    "confidence_level": 8.5
}

response = requests.post("http://127.0.0.1:5000/study_sessions", json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())
