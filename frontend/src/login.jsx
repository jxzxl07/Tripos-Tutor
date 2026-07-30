import { GoogleLogin } from '@react-oauth/google'

function Login() {
  const handleSuccess = async (credentialResponse) => {
    try {
      const res = await fetch("http://localhost:8000/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: credentialResponse.credential }),
      })
      const user = await res.json()
      alert(`Welcome, ${user.name}! (user id ${user.id})`)
    } catch (e) {
      alert("Login failed: " + e)
    }
  }

  const handleError = () => {
    alert("Login failed")
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>Tripos Tutor</h1>
        <p style={styles.subtitle}>
          AI-powered exam revision for Cambridge Computer Science.
          Practise past-paper questions and get instant, examiner-style marking.
        </p>

        <div style={{ display: "flex", justifyContent: "center" }}>
          <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
        </div>

        <p style={styles.note}>Cambridge (@cam.ac.uk) accounts only</p>
      </div>
    </div>
  )
}
  
  const styles = {
    page: {
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #1e3a8a, #0f172a)",
      fontFamily: "system-ui, sans-serif",
    },
    card: {
      background: "white",
      padding: "3rem",
      borderRadius: "16px",
      boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
      textAlign: "center",
      maxWidth: "420px",
    },
    title: { fontSize: "2.5rem", margin: "0 0 0.5rem", color: "#1e3a8a" },
    subtitle: { color: "#475569", lineHeight: 1.6, marginBottom: "2rem" },
    googleBtn: {
      background: "#1e3a8a",
      color: "white",
      border: "none",
      padding: "0.85rem 1.5rem",
      borderRadius: "8px",
      fontSize: "1rem",
      cursor: "pointer",
      width: "100%",
    },
    note: { color: "#94a3b8", fontSize: "0.85rem", marginTop: "1rem" },
  }
  
  export default Login