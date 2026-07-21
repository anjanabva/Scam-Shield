import React from 'react'

/**
 * VerdictCard
 *
 * Props:
 *   verdict  {null | { verdict:string, confidence:number, red_flags:string[], matched_pattern:string, explanation:string }}
 *   loading  {boolean}
 */

const VERDICT_CONFIG = {
  SCAM: {
    label: 'SCAM',
    icon: '🚨',
    bg: 'bg-red-950',
    border: 'border-red-600',
    badge: 'bg-red-600 text-white',
    bar: 'bg-red-500',
    text: 'text-red-400',
  },
  SUSPICIOUS: {
    label: 'SUSPICIOUS',
    icon: '⚠️',
    bg: 'bg-amber-950',
    border: 'border-amber-500',
    badge: 'bg-amber-500 text-black',
    bar: 'bg-amber-400',
    text: 'text-amber-400',
  },
  LIKELY_SAFE: {
    label: 'LIKELY SAFE',
    icon: '✅',
    bg: 'bg-emerald-950',
    border: 'border-emerald-600',
    badge: 'bg-emerald-600 text-white',
    bar: 'bg-emerald-500',
    text: 'text-emerald-400',
  },
}

const Skeleton = () => (
  <div className="animate-pulse space-y-3">
    <div className="h-8 rounded-lg bg-gray-700 w-1/2" />
    <div className="h-4 rounded bg-gray-700 w-full" />
    <div className="h-4 rounded bg-gray-700 w-3/4" />
    <div className="h-4 rounded bg-gray-700 w-5/6" />
  </div>
)

const VerdictCard = ({ verdict, loading }) => {
  if (loading) {
    return (
      <div className="rounded-xl border border-gray-700 bg-gray-900 p-5">
        <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-widest">
          Analyzing…
        </p>
        <Skeleton />
      </div>
    )
  }

  if (!verdict) {
    return (
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5 flex flex-col items-center justify-center gap-2 min-h-[140px]">
        <span className="text-3xl opacity-30">🔍</span>
        <p className="text-gray-600 text-xs text-center">
          Verdict will appear here after you paste a message
        </p>
      </div>
    )
  }

  const cfg = VERDICT_CONFIG[verdict.verdict] ?? VERDICT_CONFIG['SUSPICIOUS']
  const confidence = Math.min(Math.max(verdict.confidence ?? 0, 0), 100)

  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} p-5 space-y-4`}>

      {/* ── Verdict badge + icon ── */}
      <div className="flex items-center gap-3">
        <span className="text-2xl">{cfg.icon}</span>
        <span className={`text-xs font-bold px-3 py-1 rounded-full tracking-widest uppercase ${cfg.badge}`}>
          {cfg.label}
        </span>
      </div>

      {/* ── Confidence bar ── */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-400">Confidence</span>
          <span className={`text-sm font-bold tabular-nums ${cfg.text}`}>
            {confidence}%
          </span>
        </div>
        <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${cfg.bar}`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* ── Matched pattern ── */}
      {verdict.matched_pattern && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Matched Pattern</p>
          <p className={`text-sm font-medium ${cfg.text}`}>{verdict.matched_pattern}</p>
        </div>
      )}

      {/* ── Red flags ── */}
      {verdict.red_flags?.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Red Flags</p>
          <ul className="space-y-1">
            {verdict.red_flags.map((flag, i) => (
              <li key={i} className="flex gap-2 items-start text-xs text-gray-300">
                <span className="text-red-500 mt-0.5 flex-shrink-0">▸</span>
                {flag}
              </li>
            ))}
          </ul>
        </div>
      )}

    </div>
  )
}

export default VerdictCard