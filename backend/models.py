from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    courses = relationship("Course", back_populates="user")
    events = relationship("Event", back_populates="user")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="courses")

    topics = relationship("Topic", back_populates="course")


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    estimated_difficulty = Column(Float, nullable=False)
    days_until_deadline = Column(Integer, nullable=False)
    
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship("Course", back_populates="topics")


class StudySession(Base):
    __tablename__ = 'study_sessions'
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    duration_minutes = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    confidence_level = Column(Float)

    topic = relationship("Topic")


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="events")


db_path = Path(__file__).resolve().parent.parent / "data" / "study_data.sqlite"
engine = create_engine("sqlite:///../data/study_data.sqlite", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
