import React, { useState } from "react";
import "./App.css";

function App() {
  const [courseName, setCourseName] = useState("");
  const [description, setDescription] = useState("");
  const [courses, setCourses] = useState([]);

  const addCourse = async () => {
    if (!courseName.trim()) return;
    const response = await fetch("http://127.0.0.1:5000/courses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: courseName, description }),
    });

    const data = await response.json();
    setCourses([...courses, data]);
    setCourseName("");
    setDescription("");
  };

  const removeCourse = async (id) => {
    await fetch(`http://127.0.0.1:5000/courses/${id}`, {
      method: "DELETE",
    });

    setCourses(courses.filter((c) => c.id !== id));
  };

  return (
    <div className="container">
      <h1>Study Planner</h1>

      <div className="card">
        <h2>Add Course</h2>

        <div className="input-row">
          <input
            type="text"
            placeholder="Course name"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button onClick={addCourse}>Add</button>
        </div>
      </div>

      <div className="card">
        <h2>Courses</h2>

        {courses.length === 0 && <p>No courses yet.</p>}

        <ul>
          {courses.map((course) => (
            <li key={course.id} className="course-item">
              <div>
                <strong>{course.name}</strong>
                <p>{course.description}</p>
              </div>
              <button className="remove-btn" onClick={() => removeCourse(course.id)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;