import { useState, useEffect } from "react"

function Dashboard({ user, onBack }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(`http://localhost:8000/api/dashboard/${user.id}`)
      .then((r) => r.json()).then(setData)
  }, [user])

  if (!data)
    return <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center">Loading your progress…</div>

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 text-slate-100">
      <div className="max-w-5xl mx-auto px-8 py-10">
        <button onClick={onBack}
          className="text-sm text-blue-400 hover:text-blue-300 transition mb-6 inline-flex items-center gap-1">
          <span className="text-lg">←</span> Home
        </button>
        <h1 className="text-4xl font-bold mb-2">Your Progress</h1>
        <p className="text-slate-400 mb-10">Marks and personalised improvement points per course</p>

        {data.courses.length === 0 && (
          <p className="text-slate-400">No attempts yet — go practise some questions!</p>
        )}

        {data.courses.map((c) => (
          <div key={c.course_id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">{c.course_name}</h2>
              <span className="text-lg font-semibold text-green-400">
                {c.total_awarded} / {c.total_available}
              </span>
            </div>

            {/* Improvement summary */}
            <div className="bg-blue-950/40 border border-blue-800/50 rounded-xl p-4 mb-5">
              <p className="text-xs font-bold uppercase tracking-wide text-blue-400 mb-2">What to improve</p>
              <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-line">{c.improvement_summary}</p>
            </div>

            {/* Attempts list */}
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500 mb-2">Attempts</p>
            <div className="space-y-2">
              {c.attempts.map((a) => (
                <div key={a.attempt_id}
                  className="flex items-center justify-between bg-slate-950 border border-slate-800 rounded-lg px-4 py-2">
                  <span className="text-sm text-slate-300">
                    {a.year} · Paper {a.paper} · Q{a.question_number} ({a.part_label})
                  </span>
                  <span className="text-sm font-semibold text-slate-100">
                    {a.marks_awarded}/{a.marks_available}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Dashboard