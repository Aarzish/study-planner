import requests

topics = [
    {"name": "Algebra", "days_until_deadline": 3, "estimated_difficulty": 7},
    {"name": "Calculus", "days_until_deadline": 5, "estimated_difficulty": 5},
    {"name": "Physics", "days_until_deadline": 2, "estimated_difficulty": 8}
]

data = {
    "topics": topics,
    "available_hours": 10
}

response = requests.post("http://127.0.0.1:5000/allocate_time", json=data)
print(response.json())
