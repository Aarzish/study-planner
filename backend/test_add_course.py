import requests

data = {
    "name": "Computer Science 101",
    "description": "Intro to programming and algorithms"
}

response = requests.post("http://127.0.0.1:5000/courses", json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())
