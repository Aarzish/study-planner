from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker
from models import Course, Topic, StudySession, engine
from scheduler import allocate_time

app = Flask(__name__)

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
        
