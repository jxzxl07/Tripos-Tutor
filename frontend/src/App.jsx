import { useState } from "react"
import Login from "./login"
import Home from "./Home"
import CourseQuestions from "./CourseQuestions"
import QuestionView from "./QuestionView"
import Dashboard from "./Dashboard"

function App() {
  const [session, setSession] = useState(null)       // { token, user }
  const [screen, setScreen] = useState("home")      // home | course | question | dashboard
  const [course, setCourse] = useState(null)
  const [questionId, setQuestionId] = useState(null)

  if (!session) return <Login onLogin={setSession} />
  const user = session.user
  const logout = () => { setSession(null); setScreen("home") }

  const goHome = () => { setScreen("home"); setCourse(null); setQuestionId(null) }

  if (screen === "home") {
    return <Home user={user} onLogout={logout}
                 onPickCourse={(c) => { setCourse(c); setScreen("course") }}
                 onDashboard={() => setScreen("dashboard")} />
  }
  if (screen === "course") {
    return <CourseQuestions course={course} onBack={goHome}
                 onPickQuestion={(id) => { setQuestionId(id); setScreen("question") }} />
  }
  if (screen === "question") {
    return <QuestionView questionId={questionId} session={session}
                 onUnauthorized={logout} onBack={() => setScreen("course")} />
  }
  if (screen === "dashboard") {
    return <Dashboard session={session} onUnauthorized={logout} onBack={goHome} />
  }
}

export default App