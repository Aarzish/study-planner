import requests

data = {
    "name": "Algorithms Basics",
    "estimated_difficulty": 7,
    "days_until_deadline": 5,
    "course_id": 3  # replace with an existing course ID
}

response = requests.post("http://127.0.0.1:5000/topics", json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())

