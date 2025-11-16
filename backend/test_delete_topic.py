import requests

topic_id = 4  # change this to an existing topic id
response = requests.delete(f"http://127.0.0.1:5000/topics/{topic_id}")

print("Status Code:", response.status_code)
print("Response:", response.json())

