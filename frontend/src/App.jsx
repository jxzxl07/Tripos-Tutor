import { useState } from "react"
import Login from "./login"
import Home from "./Home"
import CourseQuestions from "./CourseQuestions"
import QuestionView from "./QuestionView"
import Dashboard from "./Dashboard"

function App() {
  const [user, setUser] = useState(null)
  const [screen, setScreen] = useState("home")      // home | course | question | dashboard
  const [course, setCourse] = useState(null)
  const [questionId, setQuestionId] = useState(null)

  if (!user) return <Login onLogin={setUser} />

  const goHome = () => { setScreen("home"); setCourse(null); setQuestionId(null) }

  if (screen === "home") {
    return <Home user={user} onLogout={() => setUser(null)}
                 onPickCourse={(c) => { setCourse(c); setScreen("course") }}
                 onDashboard={() => setScreen("dashboard")} />
  }
  if (screen === "course") {
    return <CourseQuestions course={course} onBack={goHome}
                 onPickQuestion={(id) => { setQuestionId(id); setScreen("question") }} />
  }
  if (screen === "question") {
    return <QuestionView questionId={questionId} user={user}
                 onBack={() => setScreen("course")} />
  }
  if (screen === "dashboard") {
    return <Dashboard user={user} onBack={goHome} />
  }
}

export default App