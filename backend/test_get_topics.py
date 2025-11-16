import requests

course_id = 3  # replace with your course id
response = requests.get(f"http://127.0.0.1:5000/courses/{course_id}/topics")

print("Status Code:", response.status_code)
print("Response:", response.json())

