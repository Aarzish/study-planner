import React, { useState, useEffect } from "react";

function App() {
  const [courses, setCourses] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/courses")
      .then(res => res.json())
      .then(data => setCourses(data))
      .catch(err => console.error("Error fetching courses:", err));
  }, []);

  const addCourse = async () => {
    const response = await fetch("http://127.0.0.1:5000/courses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    if (response.ok) {
      const newCourse = await response.json();
      setCourses([...courses, newCourse]);
      setName("");
      setDescription("");
    } else {
      alert("Failed to add course");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Study Planner</h1>

      <h2>Add Course</h2>
      <input
        type="text"
        placeholder="Course name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        type="text"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <button onClick={addCourse}>Add</button>

      <h2>Courses</h2>
      <ul>
        {courses.map((c) => (
          <li key={c.id}>{c.name} - {c.description}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
