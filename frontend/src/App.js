import React, { useState, useEffect } from "react";
import "./App.css";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";

function App() {
  const [courseName, setCourseName] = useState("");
  const [description, setDescription] = useState("");
  const [courses, setCourses] = useState([]);

  const [date, setDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [allEvents, setAllEvents] = useState([]);
  const [eventTitle, setEventTitle] = useState("");

  // Fetch events for selected date + all events
  const fetchEventsForDate = async (selectedDate) => {
    const dateStr = selectedDate.toISOString().split("T")[0];

    // Events for selected date
    const response = await fetch(`http://127.0.0.1:5000/events/${dateStr}`);
    const data = await response.json();
    setEvents(data);

    // Fetch ALL events (with titles + dates)
    const allResponse = await fetch("http://127.0.0.1:5000/events");
    const allData = await allResponse.json();
    setAllEvents(allData);
  };

  // Fetch initial courses + events
  useEffect(() => {
    const fetchCourses = async () => {
      const response = await fetch("http://127.0.0.1:5000/courses");
      const data = await response.json();
      setCourses(data);
    };
    fetchCourses();
    fetchEventsForDate(date);
  }, []);

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

const removeEvent = async (id) => {
  await fetch(`http://127.0.0.1:5000/events/${id}`, {
    method: "DELETE",
  });

  // Update both events (for selected date) and allEvents (for sidebar + highlights)
  setEvents(events.filter((evt) => evt.id !== id));
  setAllEvents(allEvents.filter((evt) => evt.id !== id));
};

  const handleDateClick = (selectedDate) => {
    setDate(selectedDate);
    fetchEventsForDate(selectedDate);
  };

  const addEvent = async () => {
    if (!eventTitle.trim()) return;

    const dateStr = date.toISOString().split("T")[0];

    const response = await fetch("http://127.0.0.1:5000/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: eventTitle, date: dateStr }),
    });

    const newEvent = await response.json();

    setEvents([...events, newEvent]); // for selected date view
    setAllEvents([...allEvents, newEvent]); // for sidebar + highlight
    setEventTitle("");
  };

  // Compute upcoming future events (sorted)
  const upcomingEvents = allEvents
    .filter((evt) => {
      const eventDate = new Date(evt.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return eventDate >= today;
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  // Highlight dates on calendar
  const highlightDates = allEvents.map((e) => e.date);

  return (
    <div className="layout">

      {/* LEFT SIDEBAR */}
      <div className="sidebar">
        <h2>Upcoming Events</h2>

        {upcomingEvents.length === 0 && <p>No upcoming events.</p>}

        <ul>
  {upcomingEvents.map((evt) => (
    <li key={evt.id} className="course-item">
      <div>
        <strong>{evt.title}</strong>
        <br />
        <span style={{ color: "#555" }}>{evt.date}</span>
      </div>
      <button
        className="remove-btn"
        onClick={() => removeEvent(evt.id)}
      >
        Remove
      </button>
    </li>
  ))}
</ul>
      </div>

      {/* MAIN CONTENT */}
      <div className="container">
        <h1>Study Planner</h1>

        {/* Add Course */}
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

        {/* Course List */}
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
                <button
                  className="remove-btn"
                  onClick={() => removeCourse(course.id)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Calendar Section */}
        <div className="card">
          <h2>Calendar</h2>
          <Calendar
            onClickDay={handleDateClick}
            value={date}
            tileClassName={({ date }) => {
              const dateStr = date.toISOString().split("T")[0];
              return highlightDates.includes(dateStr) ? "has-event" : null;
            }}
          />

          <div className="input-row" style={{ marginTop: "10px" }}>
            <input
              type="text"
              placeholder="Event name"
              value={eventTitle}
              onChange={(e) => setEventTitle(e.target.value)}
            />
            <button onClick={addEvent}>Add Event</button>
          </div>

          <h3 style={{ marginTop: "20px" }}>
            Events on {date.toDateString()}:
          </h3>
          <ul>
            {events.map((evt) => (
              <li key={evt.id}>{evt.title}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
