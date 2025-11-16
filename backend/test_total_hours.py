import requests

response = requests.get("http://127.0.0.1:5000/study_sessions/total_hours")

print("Status Code:", response.status_code)
print("Response:", response.json())
