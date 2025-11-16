from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from sqlalchemy.orm import sessionmaker
from models import Course, Topic, StudySession, Event, User, engine
from scheduler import allocate_time
from sqlalchemy import func
from flask_cors import CORS
from datetime import date
import datetime

# ------------------------------------
# FLASK + DB SETUP
# ------------------------------------
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "CHANGE_THIS_SECRET"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=7)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)
Session = sessionmaker(bind=engine)

# ------------------------------------
# AUTHENTICATION
# ------------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    session = Session()
    existing = session.query(User).filter_by(username=username).first()
    if existing:
        session.close()
        return jsonify({"error": "username already taken"}), 409

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, email="", password_hash=pw_hash)

    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()

    return jsonify({"message": "user created", "id": user.id}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user_id": user.id})

# ------------------------------------
# HELPERS
# ------------------------------------
def get_user(session):
    return get_jwt_identity()

# ------------------------------------
# COURSES
# ------------------------------------
@app.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    session = Session()
    user_id = get_user(session)

    courses = session.query(Course).filter_by(user_id=user_id).all()
    result = [{"id": c.id, "name": c.name, "description": c.description} for c in courses]

    session.close()
    return jsonify(result)

@app.route("/courses", methods=["POST"])
@jwt_required()
def add_course():
    data = request.get_json()
    name = data.get("name", "")
    description = data.get("description", "")

    session = Session()
    user_id = get_user(session)

    new_course = Course(name=name, description=description, user_id=user_id)
    session.add(new_course)
    session.commit()

    result = {"id": new_course.id, "name": new_course.name, "description": new_course.description}
    session.close()
    return jsonify(result), 201

@app.route("/courses/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    session = Session()
    user_id = get_user(session)

    course = session.query(Course).filter_by(id=course_id, user_id=user_id).first()
    if not course:
        session.close()
        return jsonify({"error": "Course not found"}), 404

    topics = session.query(Topic).filter_by(course_id=course_id).all()
    for t in topics:
        session.query(StudySession).filter_by(topic_id=t.id).delete()
        session.delete(t)

    session.delete(course)
    session.commit()
    session.close()

    return jsonify({"message": "Course deleted"}), 200

# ------------------------------------
# TOPICS
# ------------------------------------
@app.route("/topics", methods=["POST"])
@jwt_required()
def add_topic():
    data = request.get_json()

    name = data["name"]
    estimated_difficulty = data["estimated_difficulty"]
    days_until_deadline = data["days_until_deadline"]
    course_id = data["course_id"]

    session = Session()
    topic = Topic(
        name=name,
        estimated_difficulty=estimated_difficulty,
        days_until_deadline=days_until_deadline,
        course_id=course_id
    )

    session.add(topic)
    session.commit()
    session.close()

    return jsonify({"message": "Topic added"}), 201

@app.route("/topics/<int:topic_id>", methods=["DELETE"])
@jwt_required()
def delete_topic(topic_id):
    session = Session()
    topic = session.query(Topic).filter_by(id=topic_id).first()

    if not topic:
        session.close()
        return jsonify({"error": "Topic not found"}), 404

    session.query(StudySession).filter_by(topic_id=topic_id).delete()
    session.delete(topic)
    session.commit()
    session.close()

    return jsonify({"message": "Topic deleted"}), 200

# ------------------------------------
# EVENTS (Calendar)
# ------------------------------------
@app.route("/events", methods=["POST"])
@jwt_required()
def add_event():
    data = request.get_json()
    session = Session()
    user_id = get_user(session)

    event = Event(
        title=data["title"],
        date=data["date"],
        user_id=user_id
    )
    session.add(event)
    session.commit()

    result = {"id": event.id, "title": event.title, "date": event.date}
    session.close()
    return jsonify(result), 201

@app.route("/events", methods=["GET"])
@jwt_required()
def get_events():
    session = Session()
    user_id = get_user(session)

    events = session.query(Event).filter_by(user_id=user_id).all()
    result = [{"id": e.id, "title": e.title, "date": e.date} for e in events]

    session.close()
    return jsonify(result)

@app.route("/events/<string:event_date>", methods=["GET"])
@jwt_required()
def get_events_by_date(event_date):
    session = Session()
    user_id = get_user(session)

    events = session.query(Event).filter_by(user_id=user_id, date=event_date).all()
    result = [{"id": e.id, "title": e.title, "date": e.date} for e in events]

    session.close()
    return jsonify(result)

@app.route("/events/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    session = Session()
    user_id = get_user(session)

    event = session.query(Event).filter_by(id=event_id, user_id=user_id).first()
    if not event:
        session.close()
        return jsonify({"error": "Event not found"}), 404

    session.delete(event)
    session.commit()
    session.close()
    return jsonify({"message": "Event deleted"}), 200

@app.route("/events/past", methods=["DELETE"])
@jwt_required()
def delete_past_events():
    session = Session()
    user_id = get_user(session)

    today = date.today()
    session.query(Event).filter(Event.user_id == user_id, Event.date < today).delete()
    session.commit()
    session.close()
    return jsonify({"message": "Past events deleted"}), 200

# ------------------------------------
# STUDY SESSIONS
# ------------------------------------
@app.route("/study_sessions", methods=["POST"])
@jwt_required()
def log_study_session():
    data = request.get_json()
    session = Session()

    session_obj = StudySession(
        topic_id=data["topic_id"],
        duration_minutes=data["duration_minutes"],
        completed=data.get("completed", False),
        confidence_level=data.get("confidence_level", 0.0)
    )

    session.add(session_obj)
    session.commit()

    result = {
        "id": session_obj.id,
        "topic_id": session_obj.topic_id,
        "duration": session_obj.duration_minutes
    }

    session.close()
    return jsonify(result), 201

# ------------------------------------
# RUN
# ------------------------------------
if __name__ == "__main__":
    app.run(debug=True)