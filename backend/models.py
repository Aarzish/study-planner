from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    topics = relationship("Topic", back_populates="course")


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    estimated_difficulty = Column(Float, nullable=False)  # Scale of 1-10
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
    confidnece_level = Column(Float)  # Scale of 1-10

    topic = relationship("Topic")

engine = create_engine("sqlite:///data/study_data.sqlite", echo=True)
Base.metadata.create_all(engine)