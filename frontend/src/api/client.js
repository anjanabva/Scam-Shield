// client.js — thin API wrapper; all paths are relative (Vite proxy → FastAPI)

const BASE = '/api'

/**
 * POST /api/analyze
 * @param {string} text  – raw transcript / message pasted by the user
 * @returns {Promise<{verdict:string, confidence:number, red_flags:string[], matched_pattern:string, explanation:string}>}
 */
export async function analyze(text) {
  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`analyze failed (${res.status}): ${err}`)
  }
  return res.json()
}

/**
 * POST /api/followup
 * @param {string} question  – user's follow-up question
 * @param {string} context   – original transcript that was analyzed
 * @returns {Promise<{reply:string}>}
 */
export async function followup(question, context) {
  const res = await fetch(`${BASE}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, context }),
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`followup failed (${res.status}): ${err}`)
  }
  return res.json()
}

/**
 * GET /api/health  – optional: can be called on mount to confirm backend is up
 */
export async function healthCheck() {
  const res = await fetch(`${BASE}/health`)
  return res.ok
}