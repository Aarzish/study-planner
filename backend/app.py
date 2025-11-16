from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker
from models import Course, Topic, StudySession, Event, engine
from scheduler import allocate_time
from sqlalchemy import func
from flask_cors import CORS
from datetime import date



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
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
@app.route("/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    session = Session()
    course = session.query(Course).filter(Course.id == course_id).first()
    if not course:
        session.close()
        return jsonify({"error": "Course not found"}), 404

    # Delete associated topics and study sessions
    topics = session.query(Topic).filter(Topic.course_id == course_id).all()
    for topic in topics:
        session.query(StudySession).filter(StudySession.topic_id == topic.id).delete()
        session.delete(topic)

    session.delete(course)
    session.commit()
    session.close()
    return jsonify({"message": "Course deleted"}), 200

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
        confidence_level=confidence_level
    )
    session.add(new_session)
    session.commit()
    result = {
        "id": new_session.id,
        "topic_id": new_session.topic_id,
        "start_time": new_session.start_time,
        "duration_minutes": new_session.duration_minutes,
        "completed": new_session.completed,
        "confidence_level": new_session.confidence_level
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
            "confidence_level": s.confidence_level
        }
        result.append(session_data)
    session.close()
    return jsonify(result)

#Delete a course
# Delete an event
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    session = Session()
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        session.close()
        return jsonify({"error": "Event not found"}), 404

    session.delete(event)
    session.commit()
    session.close()
    return jsonify({"message": "Event deleted"}), 200

#Delete a topic
@app.route("/topics/<int:topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    session = Session()
    topic = session.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        session.close()
        return jsonify({"error": "Topic not found"}), 404
    # Also delete associated study sessions
    session.query(StudySession).filter(StudySession.topic_id == topic_id).delete()
    session.delete(topic)
    session.commit()
    session.close()
    return jsonify({"message": "Topic deleted"}), 200


#Get total hours studied
@app.route("/study_sessions/total_hours", methods=["GET"])
def get_total_study_hours():
    session = Session()
    total_minutes = session.query(StudySession).with_entities(
        func.sum(StudySession.duration_minutes)
    ).scalar() or 0
    session.close()
    total_hours = total_minutes / 60
    return jsonify({"total_study_hours": total_hours})

@app.route("/events", methods=["POST"])
def add_event():
    data = request.get_json()
    title = data.get("title")
    date = data.get("date")
    if not title or not date:
        return jsonify({"error": "Title and date are required"}), 400

    session = Session()
    new_event = Event(title=title, date=date)
    session.add(new_event)
    session.commit()
    result = {"id": new_event.id, "title": new_event.title, "date": new_event.date}
    session.close()
    return jsonify(result), 201

@app.route("/events/<date>", methods=["GET"])
def get_events_by_date(date):
    session = Session()
    events = session.query(Event).filter(Event.date == date).all()
    result = [{"id": e.id, "title": e.title, "date": e.date} for e in events]
    session.close()
    return jsonify(result)


@app.route("/courses/<int:course_id>/progress", methods=["GET"])
def get_course_progress(course_id):
    session = Session()
    total_minutes = session.query(StudySession).join(Topic).filter(
        Topic.course_id == course_id
    ).with_entities(func.sum(StudySession.duration_minutes)).scalar() or 0
    session.close()
    return jsonify({"course_id": course_id, "total_hours": total_minutes / 60}) 

@app.route("/topics/low_confidence", methods=["GET"])
def get_low_confidence_topics():
    session = Session()
    results = session.query(
        Topic.name,
        func.avg(StudySession.confidence_level).label("avg_confidence")
    ).join(StudySession).group_by(Topic.id).order_by("avg_confidence").limit(5).all()

    session.close()
    return jsonify([
        {"topic": r[0], "average_confidence": round(r[1], 2)} for r in results
    ])

@app.route("/study_sessions/by_date", methods=["GET"])
def get_sessions_by_date():
    session = Session()
    sessions = session.query(
        func.date(StudySession.start_time),
        func.count(StudySession.id)
    ).group_by(func.date(StudySession.start_time)).all()

    session.close()
    return jsonify([
        {"date": str(date), "session_count": count} for date, count in sessions
    ])
@app.route("/events", methods=["GET"])
def get_all_events():
    session = Session()
    events = session.query(Event).all()
    result = [{"id": e.id, "title": e.title, "date": e.date} for e in events]
    session.close()
    return jsonify(result)


@app.route("/events/past", methods=["DELETE"])
def delete_past_events():
    session = Session()
    today = date.today().isoformat()  # "YYYY-MM-DD"

    # Delete all events before today
    session.query(Event).filter(Event.date < today).delete()
    session.commit()
    session.close()

    return jsonify({"message": "Past events deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)

