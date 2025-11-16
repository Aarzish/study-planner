import requests

course_id = 3  # change this to an existing course id
response = requests.delete(f"http://127.0.0.1:5000/courses/{course_id}")

print("Status Code:", response.status_code)
print("Response:", response.json())

