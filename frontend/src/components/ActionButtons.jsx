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
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-4 flex items-center justify-center min-h-[80px]">
        <p className="text-xs text-gray-600 text-center">
          Actions will appear once a verdict is ready
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-4 space-y-3">
      <p className="text-xs text-gray-500 uppercase tracking-widest font-medium mb-1">
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
          <span className="text-lg">🚔</span>
          <span className="flex-1">Report to NCRB</span>
          <span className="text-xs opacity-70 font-normal">cybercrime.gov.in</span>
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
          <span className="text-lg">📞</span>
          <span className="flex-1">Call Cyber Helpline</span>
          <span className="text-xs opacity-70 font-normal">{PHONE}</span>
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
          <span className="text-lg">{copied ? '✅' : '📋'}</span>
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
        <div className="px-4 py-3 rounded-xl bg-gray-800 border border-gray-700 text-gray-400 text-xs leading-relaxed">
          <span className="font-semibold text-gray-300">⚡ Do not:</span> transfer money,
          share OTPs, or stay on the call. Disconnect immediately and report.
        </div>
      )}
    </div>
  )
}

export default ActionButtons