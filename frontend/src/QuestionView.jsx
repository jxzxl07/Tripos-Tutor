import { useState, useEffect } from "react"

function QuestionView({ questionId, user, onBack }) {
  const [question, setQuestion] = useState(null)
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState({})

  useEffect(() => {
    fetch(`http://localhost:8000/api/questions/${questionId}`)
      .then((r) => r.json()).then(setQuestion)
  }, [questionId])

  const submitPart = async (partId) => {
    setLoading((l) => ({ ...l, [partId]: true }))
    const res = await fetch("http://localhost:8000/api/mark", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ part_id: partId, answer: answers[partId] || "", user_id: user.id }),
    })
    const result = await res.json()
    setResults((r) => ({ ...r, [partId]: result }))
    setLoading((l) => ({ ...l, [partId]: false }))
  }

  if (!question)
    return <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center">Loading…</div>

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="flex items-center gap-4 px-6 py-4 border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-10">
        <button onClick={onBack}
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors">← Questions</button>
        <h2 className="flex-1 text-center text-base font-semibold tracking-tight">
          {question.course.replace(/-/g, " ")} · {question.year} · Paper {question.paper} Q{question.question_number}
        </h2>
        <span className="text-sm text-slate-400">{user.name}</span>
      </header>

      <div className="flex flex-1 min-h-0">
        <div className="hidden lg:block lg:w-[55%] p-4 sticky top-[65px] h-[calc(100vh-65px)]">
          <iframe title="question"
            src={`http://localhost:8000/api/questions/${questionId}/pdf#toolbar=0`}
            className="w-full h-full rounded-xl bg-white shadow-2xl ring-1 ring-slate-800" />
        </div>

        <div className="w-full lg:w-[45%] p-6 overflow-y-auto h-[calc(100vh-65px)] border-l border-slate-800">
          <h3 className="text-xl font-bold mb-5">Your Answers</h3>

          {question.parts.map((part) => {
            const r = results[part.id]
            return (
              <div key={part.id}
                className="bg-slate-900 rounded-2xl p-5 mb-5 border border-slate-800 shadow-lg">
                <div className="flex justify-between items-center mb-3">
                  <span className="font-bold text-lg">Part ({part.label})</span>
                  {part.marks != null && (
                    <span className="text-xs text-slate-300 bg-slate-950 px-3 py-1 rounded-full border border-slate-700">
                      {part.marks} marks
                    </span>
                  )}
                </div>

                <textarea
                  className="w-full min-h-[110px] p-3 rounded-lg bg-slate-950 border border-slate-700
                             text-slate-100 text-sm resize-y outline-none
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  placeholder={`Your answer to part (${part.label})…`}
                  value={answers[part.id] || ""}
                  onChange={(e) => setAnswers((a) => ({ ...a, [part.id]: e.target.value }))} />

                <button onClick={() => submitPart(part.id)} disabled={loading[part.id]}
                  className="mt-3 px-5 py-2 rounded-lg font-semibold text-sm transition
                             bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:bg-slate-700
                             disabled:cursor-default text-white shadow-md">
                  {loading[part.id] ? "Marking…" : "Submit for marking"}
                </button>

                {r && (
                  <div className="mt-4 bg-slate-950 rounded-xl p-4 border border-slate-800">
                    <div className="flex items-baseline gap-1 mb-3">
                      <span className="text-3xl font-extrabold text-green-400">{r.marks_awarded}</span>
                      <span className="text-lg text-slate-400">/ {r.marks_available}</span>
                    </div>
                    <Feedback label="✓ Strengths" color="text-green-400" text={r.strengths} />
                    <Feedback label="△ Gaps" color="text-amber-400" text={r.gaps} />
                    <Feedback label="Feedback" color="text-blue-400" text={r.feedback} />
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

function Feedback({ label, color, text }) {
  return (
    <div className="mb-3 last:mb-0">
      <p className={`text-xs font-bold uppercase tracking-wide mb-1 ${color}`}>{label}</p>
      <p className="text-sm text-slate-300 leading-relaxed">{text}</p>
    </div>
  )
}

export default QuestionView