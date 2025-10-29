from flask import Flask, request, jsonify
from scheduler import allocate_time

app = Flask(__name__)

@app.route("/")
def home():
    return "If you see this, the backend is running."

@app.route("/api/schedule", methods=["POST"])
def make_schedule():
    data = request.get_json()
    topics = data.get("topics", [])
    available_hours = data.get("available_hours", 5)
    allocations = allocate_time(topics, available_hours)
    return jsonify({
        "topics": [t["name"] for t in topics],
        "allocations": allocations
    })

if __name__ == "__main__":
    app.run(debug=True)

