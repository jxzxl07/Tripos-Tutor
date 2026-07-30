import { useState, useEffect } from "react"

function CourseQuestions({ course, onBack, onPickQuestion }) {
  const [questions, setQuestions] = useState([])

  useEffect(() => {
    fetch(`http://localhost:8000/api/courses/${course.slug}/questions`)
      .then((r) => r.json())
      .then(setQuestions)
  }, [course])

  return (
    <div style={s.page}>
      <button style={s.back} onClick={onBack}>← Courses</button>
      <h1 style={s.title}>{course.name}</h1>
      <div style={s.grid}>
        {questions.map((q) => (
          <button key={q.id} style={s.qBtn} onClick={() => onPickQuestion(q.id)}>
            {q.year} · Paper {q.paper} · Q{q.question_number}
          </button>
        ))}
      </div>
    </div>
  )
}

const s = {
  page: { minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", fontFamily: "system-ui,sans-serif", padding: "2rem" },
  back: { background: "none", color: "#93c5fd", border: "none", fontSize: "1rem", cursor: "pointer", marginBottom: "1rem" },
  title: { marginTop: 0 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(200px,1fr))", gap: "0.75rem" },
  qBtn: { background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155", padding: "1rem", borderRadius: "8px", cursor: "pointer" },
}

export default CourseQuestions