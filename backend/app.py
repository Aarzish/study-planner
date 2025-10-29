from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker
from models import Course, Topic, StudySession, engine
from scheduler import allocate_time

app = Flask(__name__)

#Connects Flask to the database
Session = sessionmaker(bind=engine)

@app.route("/")
def home():
    return jsonify({"message": "If you see this, the backend is running."})

#Get all courses
@app.route("/courses", methods=["GET"])
def get_courses():
    session = Session()
    courses = session.query(Course).all()
    result = []
    for course in courses:
        course_data = {
            "id": course.id,
            "name": course.name,
            "description": course.description
        }
        result.append(course_data)
    session.close()
    return jsonify(result)
        

#Add a new course
@app.route("/courses", methods=["POST"])
def add_course():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Course name is required"}), 400
    description = data.get("description", "")
    session = Session()
    new_course = Course(name=data["name"], description=data.get("description", ""))
    session.add(new_course)
    session.commit()
    result = {
        "id": new_course.id,
        "name": new_course.name,
        "description": new_course.description
    }
    session.close()
    return jsonify(result), 201


# Allocates study time
@app.route("/allocate_time", methods=["POST"])
def allocate_study_time():
    """
    Takes a list of topics with their urgency and difficulty, and available study hours,
    returns allocated study hours per topic.
    """
    data = request.get_json()
    topics = data.get("topics", [])
    available_hours = data.get("available_hours", 0)
    if not topics or available_hours <= 0:
        return jsonify({"error": "Enter topics and available hours"}), 400
    
    allocations = allocate_time(topics, available_hours)
    
    #combine topics with their allocated time
    result = []
    for topic, hours in zip(topics, allocations):
        result.append({
            "topic": topic["name"],
            "days_until_deadline": topic["days_until_deadline"],
            "estimated_difficulty": topic["estimated_difficulty"],
            "allocated_hours": hours
        })

    return jsonify({"allocations": result})


if __name__ == "__main__":
    app.run(debug=True)