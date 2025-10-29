from models import Course, Topic, StudySession, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Create a course
math = Course(name="Math", description="Core mathematics")

# Create a topic linked to that course
algebra = Topic(name="Algebra", estimated_difficulty=7.0, days_until_deadline=3, course=math)

# Add and commit to database
session.add(math)
session.add(algebra)
session.commit()

print("Added course and topic successfully!")

# Query back to check
for course in session.query(Course).all():
    print(f"Course: {course.name}")
    for topic in course.topics:
        print(f"  └─ Topic: {topic.name} (Difficulty {topic.estimated_difficulty})")
