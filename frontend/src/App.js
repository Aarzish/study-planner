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
  const [reminder, setReminder] = useState("none");

  // Fetch events for selected date + all events
  const fetchEventsForDate = async (selectedDate) => {
    const dateStr = selectedDate.toISOString().split("T")[0];

    const response = await fetch(`http://127.0.0.1:5000/events/${dateStr}`);
    const data = await response.json();
    setEvents(data);

    const allResponse = await fetch("http://127.0.0.1:5000/events");
    const allData = await allResponse.json();
    setAllEvents(allData);
  };

  // Ask for browser notification permission
  useEffect(() => {
    if ("Notification" in window) {
      Notification.requestPermission();
    }
  }, []);

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

    setEvents(events.filter((evt) => evt.id !== id));
    setAllEvents(allEvents.filter((evt) => evt.id !== id));
  };

  const handleDateClick = (selectedDate) => {
    setDate(selectedDate);
    fetchEventsForDate(selectedDate);
  };

  // Reminder Scheduling Logic
  const scheduleReminder = (dateStr, title, reminderType) => {
    if (reminderType === "none") return;

    const eventDate = new Date(dateStr);
    let notifyTime = new Date(eventDate);

    if (reminderType === "day") {
      notifyTime.setHours(9, 0, 0);
    } else {
      notifyTime.setDate(notifyTime.getDate() - parseInt(reminderType));
      notifyTime.setHours(9, 0, 0);
    }

    const timeout = notifyTime - Date.now();

    if (timeout > 0) {
      setTimeout(() => {
        if (Notification.permission === "granted") {
          new Notification("Study Planner Reminder", {
            body: `${title} is coming up!`,
            icon: "/favicon.ico",
          });
        }
      }, timeout);
    }
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

    setEvents([...events, newEvent]);
    setAllEvents([...allEvents, newEvent]);

    // Schedule the reminder
    scheduleReminder(dateStr, eventTitle, reminder);

    setEventTitle("");
    setReminder("none");
  };

  const upcomingEvents = allEvents
    .filter((evt) => {
      const eventDate = new Date(evt.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return eventDate >= today;
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  const highlightDates = allEvents.map((e) => e.date);

  const deletePastEvents = async () => {
    await fetch("http://127.0.0.1:5000/events/past", { method: "DELETE" });
    fetchEventsForDate(date);
  };

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
              <button className="remove-btn" onClick={() => removeEvent(evt.id)}>
                Remove
              </button>
            </li>
          ))}
        </ul>

        <button className="clear-btn" onClick={deletePastEvents}>
          Clear Past Events
        </button>
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
              const classes = [];
              if (highlightDates.includes(dateStr)) {
                classes.push("has-event");
              }
              return classes.join(" ");
            }}
          />

          <div className="input-row" style={{ marginTop: "10px" }}>
            <input
              type="text"
              placeholder="Event name"
              value={eventTitle}
              onChange={(e) => setEventTitle(e.target.value)}
            />

            <select
              value={reminder}
              onChange={(e) => setReminder(e.target.value)}
              className="reminder-select"
            >
              <option value="none">No reminder</option>
              <option value="day">On the day</option>
              <option value="1">1 day before</option>
              <option value="3">3 days before</option>
              <option value="7">1 week before</option>
            </select>

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
