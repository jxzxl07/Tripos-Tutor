import { useState } from "react"
import Login from "./login"
import Home from "./Home"
import CourseQuestions from "./CourseQuestions"
import QuestionView from "./QuestionView"

function App() {
  const [user, setUser] = useState(null)
  const [screen, setScreen] = useState("home")      // home | course | question
  const [course, setCourse] = useState(null)         // selected course
  const [questionId, setQuestionId] = useState(null) // selected question

  if (!user) return <Login onLogin={setUser} />

  const goHome = () => { setScreen("home"); setCourse(null); setQuestionId(null) }

  if (screen === "home") {
    return <Home user={user} onLogout={() => setUser(null)}
                 onPickCourse={(c) => { setCourse(c); setScreen("course") }} />
  }
  if (screen === "course") {
    return <CourseQuestions course={course} onBack={goHome}
                 onPickQuestion={(id) => { setQuestionId(id); setScreen("question") }} />
  }
  if (screen === "question") {
    return <QuestionView questionId={questionId} user={user}
                 onBack={() => setScreen("course")} />
  }
}

export default App