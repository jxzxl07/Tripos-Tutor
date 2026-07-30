import { useState, useEffect } from "react"

function QuestionView({ questionId, user, onBack }) {
  const [question, setQuestion] = useState(null)
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState({})

  useEffect(() => {
    fetch(`http://localhost:8000/api/questions/${questionId}`)
      .then((r) => r.json())
      .then(setQuestion)
  }, [questionId])

  const submitPart = async (partId) => {
    setLoading((l) => ({ ...l, [partId]: true }))
    const res = await fetch("http://localhost:8000/api/mark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ part_id: partId, answer: answers[partId] || "" }),
    })
    const result = await res.json()
    setResults((r) => ({ ...r, [partId]: result }))
    setLoading((l) => ({ ...l, [partId]: false }))
  }

  if (!question) return <div style={s.loading}>Loading…</div>

  return (
    <div style={s.page}>
      {/* Top bar */}
      <div style={s.topbar}>
        <button style={s.back} onClick={onBack}>← Questions</button>
        <h2 style={s.title}>
          {question.course.replace(/-/g, " ")} · {question.year} · Paper {question.paper} Q{question.question_number}
        </h2>
        <span style={s.user}>{user.name}</span>
      </div>

      {/* Two-column layout */}
      <div style={s.columns}>
        {/* Left: the PDF */}
        <div style={s.pdfCol}>
          <iframe
            title="question"
            src={`http://localhost:8000/api/questions/${questionId}/pdf#toolbar=0`}
            style={s.pdf}
          />
        </div>

        {/* Right: answers */}
        <div style={s.answerCol}>
          <h3 style={s.answerHeading}>Your Answers</h3>
          {question.parts.map((part) => {
            const result = results[part.id]
            return (
              <div key={part.id} style={s.partCard}>
                <div style={s.partHeader}>
                  <span style={s.partLabel}>Part ({part.label})</span>
                  {part.marks ? <span style={s.partMarks}>{part.marks} marks</span> : null}
                </div>
                <textarea
                  style={s.textarea}
                  placeholder={`Your answer to part (${part.label})…`}
                  value={answers[part.id] || ""}
                  onChange={(e) => setAnswers((a) => ({ ...a, [part.id]: e.target.value }))}
                />
                <button
                  style={{ ...s.submit, ...(loading[part.id] ? s.submitDisabled : {}) }}
                  onClick={() => submitPart(part.id)}
                  disabled={loading[part.id]}
                >
                  {loading[part.id] ? "Marking…" : "Submit for marking"}
                </button>

                {result && (
                  <div style={s.result}>
                    <div style={s.markRow}>
                      <span style={s.mark}>{result.marks_awarded}</span>
                      <span style={s.markOutOf}>/ {result.marks_available}</span>
                    </div>
                    <div style={s.feedbackBlock}>
                      <p style={s.fbLabel}>✓ Strengths</p>
                      <p style={s.fbText}>{result.strengths}</p>
                    </div>
                    <div style={s.feedbackBlock}>
                      <p style={s.fbLabelGap}>△ Gaps</p>
                      <p style={s.fbText}>{result.gaps}</p>
                    </div>
                    <div style={s.feedbackBlock}>
                      <p style={s.fbLabelInfo}>Feedback</p>
                      <p style={s.fbText}>{result.feedback}</p>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

const s = {
  loading: { minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "system-ui,sans-serif" },
  page: { minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", fontFamily: "system-ui,sans-serif", display: "flex", flexDirection: "column" },

  topbar: { display: "flex", alignItems: "center", gap: "1.5rem", padding: "1rem 1.5rem", borderBottom: "1px solid #1e293b", background: "#0b1120" },
  back: { background: "none", color: "#60a5fa", border: "none", fontSize: "0.95rem", cursor: "pointer", padding: 0 },
  title: { margin: 0, fontSize: "1.1rem", fontWeight: 600, flex: 1 },
  user: { color: "#94a3b8", fontSize: "0.9rem" },

  columns: { display: "flex", flex: 1, minHeight: 0 },

  pdfCol: { flex: "1 1 55%", padding: "1rem", background: "#0f172a", position: "sticky", top: 0, height: "calc(100vh - 65px)" },
  pdf: { width: "100%", height: "100%", border: "none", borderRadius: "8px", background: "white" },

  answerCol: { flex: "1 1 45%", padding: "1.5rem", overflowY: "auto", height: "calc(100vh - 65px)", borderLeft: "1px solid #1e293b" },
  answerHeading: { marginTop: 0, fontSize: "1.3rem" },

  partCard: { background: "#1e293b", borderRadius: "12px", padding: "1.25rem", marginBottom: "1.25rem", border: "1px solid #334155" },
  partHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" },
  partLabel: { fontWeight: 700, fontSize: "1.05rem" },
  partMarks: { color: "#94a3b8", fontSize: "0.85rem", background: "#0f172a", padding: "0.2rem 0.6rem", borderRadius: "999px" },

  textarea: { width: "100%", boxSizing: "border-box", minHeight: "110px", padding: "0.75rem", borderRadius: "8px", border: "1px solid #475569", background: "#0f172a", color: "#e2e8f0", fontFamily: "inherit", fontSize: "0.95rem", resize: "vertical" },
  submit: { background: "#2563eb", color: "white", border: "none", padding: "0.6rem 1.4rem", borderRadius: "8px", cursor: "pointer", marginTop: "0.75rem", fontSize: "0.95rem", fontWeight: 600 },
  submitDisabled: { background: "#475569", cursor: "default" },

  result: { marginTop: "1rem", background: "#0f172a", borderRadius: "10px", padding: "1rem", border: "1px solid #334155" },
  markRow: { display: "flex", alignItems: "baseline", gap: "0.3rem", marginBottom: "1rem" },
  mark: { fontSize: "2rem", fontWeight: 800, color: "#4ade80", lineHeight: 1 },
  markOutOf: { fontSize: "1.1rem", color: "#94a3b8" },
  feedbackBlock: { marginBottom: "0.85rem" },
  fbLabel: { margin: "0 0 0.2rem", fontWeight: 700, color: "#4ade80", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.03em" },
  fbLabelGap: { margin: "0 0 0.2rem", fontWeight: 700, color: "#fbbf24", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.03em" },
  fbLabelInfo: { margin: "0 0 0.2rem", fontWeight: 700, color: "#60a5fa", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.03em" },
  fbText: { margin: 0, lineHeight: 1.55, fontSize: "0.92rem", color: "#cbd5e1" },
}

export default QuestionView