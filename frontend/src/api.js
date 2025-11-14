const API_URL = "http://127.0.0.1:5000";

export async function getCourses() {
  const res = await fetch(`${API_URL}/courses`);
  return res.json();
}

export async function addCourse(course) {
  const res = await fetch(`${API_URL}/courses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(course),
  });
  return res.json();
}

