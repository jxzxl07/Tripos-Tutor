import { useState, useEffect } from "react"

function Home({ user, onLogout, onPickCourse, onDashboard }) {
  const [courses, setCourses] = useState([])

  useEffect(() => {
    fetch("http://localhost:8000/api/courses")
      .then((r) => r.json()).then(setCourses)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-slate-900 to-slate-950 text-slate-100">
      <div className="max-w-7xl mx-auto px-8 py-10">
        <header className="flex items-center justify-between mb-16">
          <h1 className="text-2xl font-bold tracking-tight">Tripos Tutor</h1>
          <div className="flex items-center gap-4">
            <span className="text-slate-300 text-sm">{user.name}</span>
            <button onClick={onDashboard}
              className="text-sm bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg transition-colors">
              My Progress
            </button>
            <button onClick={onLogout}
              className="text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700
                         px-4 py-2 rounded-lg transition-colors">Log out</button>
          </div>
        </header>

        <div className="text-center mb-14">
          <h2 className="text-4xl font-bold mb-3 tracking-tight">Choose a course to practise</h2>
          <p className="text-slate-400 text-lg">Past-paper questions with instant, examiner-style AI marking</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {courses.map((c) => (
            <button key={c.id} onClick={() => onPickCourse(c)}
              className="group bg-slate-800/40 hover:bg-slate-800 border border-slate-700/80
                         hover:border-blue-500 rounded-2xl p-6 text-left transition-all duration-200
                         hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-500/10 min-h-[110px] flex flex-col justify-between">
              <span className="font-semibold text-lg leading-snug">{c.name}</span>
              <span className="text-slate-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all text-xl self-end">→</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home