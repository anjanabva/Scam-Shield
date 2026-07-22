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
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-red-500">
        <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" clipRule="evenodd" />
      </svg>
    ),
    bg: 'bg-red-950/40 backdrop-blur-md',
    border: 'border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.15)]',
    badge: 'bg-red-500/20 text-red-400 border border-red-500/30',
    bar: 'bg-gradient-to-r from-red-600 to-red-400',
    text: 'text-red-400',
  },
  SUSPICIOUS: {
    label: 'SUSPICIOUS',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-amber-500">
        <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" clipRule="evenodd" />
      </svg>
    ),
    bg: 'bg-amber-950/40 backdrop-blur-md',
    border: 'border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.15)]',
    badge: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
    bar: 'bg-gradient-to-r from-amber-600 to-amber-400',
    text: 'text-amber-400',
  },
  LIKELY_SAFE: {
    label: 'LIKELY SAFE',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-emerald-500">
        <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12Zm13.36-1.814a.75.75 0 1 0-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 0 0-1.06 1.06l2.25 2.25a.75.75 0 0 0 1.14-.094l3.75-5.25Z" clipRule="evenodd" />
      </svg>
    ),
    bg: 'bg-emerald-950/40 backdrop-blur-md',
    border: 'border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.15)]',
    badge: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    bar: 'bg-gradient-to-r from-emerald-600 to-emerald-400',
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
  if (loading && !verdict) {
    return (
      <div className="rounded-xl glass-panel p-5">
        <p className="text-xs text-indigo-400/70 mb-3 font-semibold uppercase tracking-widest">
          Analyzing threat…
        </p>
        <Skeleton />
      </div>
    )
  }

  if (!verdict) {
    return (
      <div className="rounded-xl glass-panel p-5 flex flex-col items-center justify-center gap-3 min-h-[140px]">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-gray-600">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 15.75l-2.489-2.489m0 0a3.375 3.375 0 10-4.773-4.773 3.375 3.375 0 004.774 4.774zM21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-gray-500 text-xs text-center font-medium">
          Awaiting input for analysis
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
        {cfg.icon}
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