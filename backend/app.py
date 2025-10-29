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

#Add a new topic
@app.route("/topics", methods=["POST"])
def add_topic():
    data = request.get_json()
    name = data.get("name")
    estimated_difficulty = data.get("estimated_difficulty")
    days_until_deadline = data.get("days_until_deadline")
    course_id = data.get("course_id")

    if not all([name, estimated_difficulty, days_until_deadline, course_id]):
        return jsonify({"error": "All fields are required"}), 400

    session = Session()
    new_topic = Topic(
        name=name,
        estimated_difficulty=estimated_difficulty,
        days_until_deadline=days_until_deadline,
        course_id=course_id
    )
    session.add(new_topic)
    session.commit()
    result = {
        "id": new_topic.id,
        "name": new_topic.name,
        "estimated_difficulty": new_topic.estimated_difficulty,
        "days_until_deadline": new_topic.days_until_deadline,
        "course_id": new_topic.course_id
    }
    session.close()
    return jsonify(result), 201

#Get all topics for a specific course
@app.route("/courses/<int:course_id>/topics", methods=["GET"])
def get_topics(course_id):
    sessiom = Session()
    topics = sessiom.query(Topic).filter(Topic.course_id == course_id).all()
    result = []
    for topic in topics:
        topic_data = {
            "id": topic.id,
            "name": topic.name,
            "estimated_difficulty": topic.estimated_difficulty,
            "days_until_deadline": topic.days_until_deadline,
            "course_id": topic.course_id
        }
        result.append(topic_data)
    sessiom.close()
    return jsonify(result)


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

#Log the study session
@app.route("/study_sessions", methods=["POST"])
def log_study_session():
    data = request.get_json()
    topic_id = data.get("topic_id")
    duration_minutes = data.get("duration_minutes")
    completed = data.get("completed", False)
    confidence_level = data.get("confidence_level",0.0)

    if not all([topic_id, duration_minutes]):
        return jsonify({"error": "topic_id and duration_minutes are required"}), 400

    session = Session()
    new_session = StudySession(
        topic_id=topic_id,
        duration_minutes=duration_minutes,
        completed=completed,
        confidnece_level=confidence_level
    )
    session.add(new_session)
    session.commit()
    result = {
        "id": new_session.id,
        "topic_id": new_session.topic_id,
        "start_time": new_session.start_time,
        "duration_minutes": new_session.duration_minutes,
        "completed": new_session.completed,
        "confidence_level": new_session.confidnece_level
    }
    session.close()
    return jsonify(result), 201

#Get all study sessions
@app.route("/study_sessions", methods=["GET"])
def get_study_sessions():
    session = Session()
    sessions = session.query(StudySession).all()
    result = []
    for s in sessions:
        session_data = {
            "id": s.id,
            "topic_id": s.topic_id,
            "start_time": s.start_time,
            "duration_minutes": s.duration_minutes,
            "completed": s.completed,
            "confidence_level": s.confidnece_level
        }
        result.append(session_data)
    session.close()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)