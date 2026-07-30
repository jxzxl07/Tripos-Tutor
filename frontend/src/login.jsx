import { GoogleLogin } from '@react-oauth/google'

function Login({ onLogin }) {
  const handleSuccess = async (credentialResponse) => {
    try {
      const res = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: credentialResponse.credential }),
      })
      if (res.status === 403) {
        alert("Please sign in with your Cambridge (@cam.ac.uk) account.")
        return
      }
      const user = await res.json()
      onLogin(user)
    } catch (e) {
      alert("Login failed: " + e)
    }
  }
  const handleError = () => alert("Login failed")

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-950 via-slate-900 to-slate-950 px-4">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4 shadow-lg shadow-blue-500/30">
            <span className="text-3xl font-bold text-white">T</span>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight">Tripos Tutor</h1>
        </div>

        {/* Card */}
        <div className="bg-white/95 backdrop-blur rounded-3xl p-8 shadow-2xl">
          <p className="text-slate-600 text-center leading-relaxed mb-8">
            AI-powered exam revision for Cambridge Computer Science. Practise past-paper
            questions and get instant, examiner-style marking.
          </p>

          <div className="flex justify-center mb-6">
            <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
          </div>

          <div className="flex items-center gap-3 text-slate-400 text-xs">
            <div className="flex-1 h-px bg-slate-200" />
            <span>Cambridge accounts only</span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>
        </div>

        {/* Feature hints */}
        <div className="grid grid-cols-3 gap-3 mt-6 text-center">
          {[
            ["230+", "Past questions"],
            ["All", "IB courses"],
            ["AI", "Accurate marking"],
          ].map(([big, small]) => (
            <div key={small} className="bg-white/5 border border-white/10 rounded-xl py-3">
              <p className="text-xl font-bold text-white">{big}</p>
              <p className="text-xs text-slate-400 mt-0.5">{small}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Login