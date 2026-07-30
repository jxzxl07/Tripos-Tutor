import { useState, useEffect } from "react"

function CourseQuestions({ course, onBack, onPickQuestion }) {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/courses/${course.slug}/questions`)
      .then((r) => r.json())
      .then((data) => { setQuestions(data); setLoading(false) })
  }, [course])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 text-slate-100">
      <div className="max-w-7xl mx-auto px-8 py-10">
        <button onClick={onBack}
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors mb-8 inline-flex items-center gap-1">
          <span className="text-lg">←</span> Courses
        </button>

        <div className="mb-10">
          <p className="text-blue-400 text-sm font-semibold uppercase tracking-widest mb-2">Practice</p>
          <h1 className="text-5xl font-bold tracking-tight">{course.name}</h1>
          <p className="text-slate-400 mt-3 text-lg">{questions.length} past-paper questions available</p>
        </div>

        {loading ? (
          <p className="text-slate-400">Loading questions…</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {questions.map((q) => (
              <button key={q.id} onClick={() => onPickQuestion(q.id)}
                className="group relative bg-slate-800/40 hover:bg-slate-800 border border-slate-700/80
                           hover:border-blue-500 rounded-2xl p-6 text-left transition-all duration-200
                           hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-500/10">
                <p className="text-xs text-blue-400 font-semibold uppercase tracking-widest mb-2">{q.year}</p>
                <div className="flex items-end justify-between">
                  <div>
                    <p className="font-semibold text-xl text-slate-100 leading-tight">Paper {q.paper}</p>
                    <p className="text-slate-400 mt-0.5">Question {q.question_number}</p>
                  </div>
                  <span className="text-slate-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all text-2xl">→</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default CourseQuestions