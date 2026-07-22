import React from 'react'

const TrendingPanel = ({ campaigns }) => {
  if (!campaigns || campaigns.length === 0) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-md rounded-xl border border-gray-800 p-4">
        <h2 className="text-sm font-semibold tracking-wide text-gray-400 uppercase mb-1">
          Active Campaigns
        </h2>
        <p className="text-xs text-gray-500">No trending scams detected recently.</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/60 backdrop-blur-md rounded-xl border border-rose-900/30 p-4 shadow-[0_0_15px_rgba(225,29,72,0.1)]">
      <div className="flex items-center gap-2 mb-3">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-500 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-600"></span>
        </span>
        <h2 className="text-sm font-bold tracking-wide text-rose-500 uppercase">
          Live Fraud Campaigns
        </h2>
      </div>
      
      <div className="space-y-3">
        {campaigns.map((c) => (
          <div key={c.campaign_id} className="bg-gray-950/50 rounded-lg p-3 border border-gray-800 hover:border-gray-700 transition-colors">
            <div className="flex justify-between items-start mb-1">
              <h3 className="text-sm font-medium text-gray-200 line-clamp-1 flex-1 pr-2">
                {c.matched_pattern}
              </h3>
              <span className="px-1.5 py-0.5 bg-rose-500/10 text-rose-400 text-[10px] font-bold rounded">
                {c.count} Reports
              </span>
            </div>
            
            <p className="text-xs text-gray-500 italic line-clamp-2 mb-2">
              "{c.preview}"
            </p>
            
            <div className="flex flex-wrap gap-1">
              {c.top_red_flags.slice(0, 3).map((flag) => (
                <span key={flag} className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-800 text-gray-400 capitalize">
                  {flag.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
            
            <div className="mt-2 text-[10px] text-gray-600 flex justify-between">
              <span>First seen: {new Date(c.first_seen).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              <span>Span: {c.window_hours}h</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TrendingPanel
