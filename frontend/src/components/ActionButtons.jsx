import React, { useState } from 'react'

/**
 * ActionButtons
 *
 * Props:
 *   verdict  {null | { verdict:string, ... }}
 */

const NCRB_URL = 'https://cybercrime.gov.in'
const PHONE = '1930'

const ActionButtons = ({ verdict }) => {
  const [copied, setCopied] = useState(false)

  const isScam = verdict?.verdict === 'SCAM'
  const isSuspicious = verdict?.verdict === 'SUSPICIOUS'
  const showActions = isScam || isSuspicious

  const handleCopyEvidence = async () => {
    if (!verdict) return
    const lines = [
      `VERDICT: ${verdict.verdict}`,
      `CONFIDENCE: ${verdict.confidence}%`,
      verdict.matched_pattern ? `MATCHED PATTERN: ${verdict.matched_pattern}` : null,
      verdict.red_flags?.length
        ? `RED FLAGS:\n${verdict.red_flags.map(f => `  • ${f}`).join('\n')}`
        : null,
      verdict.explanation ? `\nEXPLANATION:\n${verdict.explanation}` : null,
    ]
      .filter(Boolean)
      .join('\n')

    try {
      await navigator.clipboard.writeText(lines)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback: open a pre-filled mail
      window.open(
        `mailto:?subject=Scam%20Evidence&body=${encodeURIComponent(lines)}`,
        '_blank',
      )
    }
  }

  if (!verdict) {
    return (
      <div className="rounded-xl glass-panel p-4 flex flex-col items-center justify-center min-h-[80px]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-gray-700 mb-2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-xs text-gray-500 font-medium text-center">
          Actions will appear once a verdict is ready
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-xl glass-panel p-4 space-y-3">
      <p className="text-[10px] text-indigo-400/70 uppercase tracking-widest font-bold mb-2">
        Recommended Actions
      </p>

      {/* ── Report to NCRB ── */}
      {showActions && (
        <a
          id="btn-report-ncrb"
          href={NCRB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="
            flex items-center gap-3 w-full px-4 py-3 rounded-xl
            bg-red-600 hover:bg-red-500 active:bg-red-700
            text-white text-sm font-semibold
            transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]
          "
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5 text-white/90">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.315 48.315 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
          </svg>
          <span className="flex-1">Report to NCRB</span>
          <span className="text-xs text-red-200/80 font-medium">cybercrime.gov.in</span>
        </a>
      )}

      {/* ── Call 1930 ── */}
      {showActions && (
        <a
          id="btn-call-1930"
          href={`tel:${PHONE}`}
          className="
            flex items-center gap-3 w-full px-4 py-3 rounded-xl
            bg-orange-600 hover:bg-orange-500 active:bg-orange-700
            text-white text-sm font-semibold
            transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]
          "
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5 text-white/90">
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-2.896-1.596-5.54-4.24-7.136-7.136l1.292-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
          </svg>
          <span className="flex-1">Call Cyber Helpline</span>
          <span className="text-xs text-orange-200/80 font-medium">{PHONE}</span>
        </a>
      )}

      {/* ── Copy evidence ── */}
      {verdict && (
        <button
          id="btn-copy-evidence"
          onClick={handleCopyEvidence}
          className="
            flex items-center gap-3 w-full px-4 py-3 rounded-xl
            bg-gray-800 hover:bg-gray-700 active:bg-gray-900
            border border-gray-700 text-gray-200 text-sm font-medium
            transition-all duration-150 hover:scale-[1.02] active:scale-[0.98]
          "
        >
          {copied ? (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5 text-emerald-400">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-gray-400">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
            </svg>
          )}
          <span className="flex-1">{copied ? 'Copied!' : 'Copy Evidence'}</span>
          <span className="text-xs text-gray-500 font-normal">save for report</span>
        </button>
      )}

      {/* ── Safe message tip ── */}
      {verdict?.verdict === 'LIKELY_SAFE' && (
        <div className="px-4 py-3 rounded-xl bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs leading-relaxed">
          <span className="font-semibold">Looks safe.</span> Stay alert — official agencies never
          demand money over calls or ask you to stay on video.
        </div>
      )}

      {/* ── Scam tip ── */}
      {showActions && (
        <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-400 text-xs leading-relaxed backdrop-blur-sm">
          <span className="font-bold text-red-400 mr-1">Do not:</span>
          transfer money, share OTPs, or stay on the call. Disconnect immediately and report.
        </div>
      )}
    </div>
  )
}

export default ActionButtons