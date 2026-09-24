// Calls a protected API route with the session token.
// A 401 means the session expired or is invalid, so we sign the user out.
export async function authFetch(path, session, onUnauthorized, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { ...(options.headers || {}), Authorization: `Bearer ${session.token}` },
  })
  if (res.status === 401) {
    onUnauthorized()
    throw new Error("Session expired - please sign in again")
  }
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json()
}
