import { useState, useEffect } from "react"

function Home({ user, onLogout, onPickCourse }) {
  const [courses, setCourses] = useState([])

  useEffect(() => {
    fetch("http://localhost:8000/api/courses")
      .then((r) => r.json())
      .then(setCourses)
  }, [])

  return (
    <div style={s.page}>
      <div style={s.header}>
        <h1 style={s.brand}>Tripos Tutor</h1>
        <div>
          <span style={s.name}>{user.name}</span>
          <button style={s.logout} onClick={onLogout}>Log out</button>
        </div>
      </div>

      <p style={s.prompt}>Choose a course to practise:</p>
      <div style={s.grid}>
        {courses.map((c) => (
          <button key={c.id} style={s.courseBtn} onClick={() => onPickCourse(c)}>
            {c.name}
          </button>
        ))}
      </div>
    </div>
  )
}

const s = {
  page: { minHeight: "100vh", background: "linear-gradient(135deg,#1e3a8a,#0f172a)", color: "#e2e8f0", fontFamily: "system-ui,sans-serif", padding: "2rem" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" },
  brand: { margin: 0, fontSize: "1.8rem" },
  name: { marginRight: "1rem" },
  logout: { background: "#334155", color: "white", border: "none", padding: "0.5rem 1rem", borderRadius: "6px", cursor: "pointer" },
  prompt: { fontSize: "1.1rem", marginBottom: "1rem" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(240px,1fr))", gap: "1rem" },
  courseBtn: { background: "white", color: "#1e3a8a", border: "none", padding: "1.2rem", borderRadius: "10px", fontSize: "1rem", fontWeight: 600, cursor: "pointer", textAlign: "left" },
}

export default Home