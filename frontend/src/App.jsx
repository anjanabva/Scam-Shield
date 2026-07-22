import React, { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import VerdictCard from './components/VerdictCard'
import ActionButtons from './components/ActionButtons'
import TrendingPanel from './components/TrendingPanel'
import { getTrending } from './api/client'

const App = () => {
  // Shared state passed down as props
  const [messages, setMessages] = useState([])      // chat history
  const [verdict, setVerdict] = useState(null)      // { verdict, confidence, red_flags, matched_pattern, explanation }
  const [loading, setLoading] = useState(false)     // API in-flight
  const [trendingCampaigns, setTrendingCampaigns] = useState([]) // live campaigns

  // Fetch trending campaigns periodically
  React.useEffect(() => {
    const fetchTrending = async () => {
      try {
        const data = await getTrending()
        setTrendingCampaigns(data.campaigns || [])
      } catch (err) {
        console.error('Failed to fetch trending campaigns:', err)
      }
    }

    // Initial fetch
    fetchTrending()

    // Poll every 1 hour
    const interval = setInterval(fetchTrending, 3600000)
    return () => clearInterval(interval)
  }, [])

  const handleReset = () => {
    setMessages([])
    setVerdict(null)
    setLoading(false)
  }

  return (
    <div className="min-h-screen md:h-screen md:overflow-hidden text-white flex flex-col bg-transparent">

      {/* ── Header ── */}
      <header className="border-b border-white/10 glass-panel px-6 py-4 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-indigo-500">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
        </svg>
        <div>
          <h1 className="text-lg font-bold tracking-tight leading-none">Scam Shield</h1>
          <p className="text-xs text-gray-500">AI-Powered Fraud Detection</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {verdict && (
            <button
              id="btn-reset"
              onClick={handleReset}
              className="text-xs text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg border border-white/10 hover:border-white/30 bg-white/5 backdrop-blur-sm flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-3 h-3">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              New analysis
            </button>
          )}
          <span className="text-xs text-indigo-400/80 font-medium hidden sm:block tracking-wider uppercase">ET AI Hackathon 2026</span>
        </div>
      </header>

      {/* ── Main layout ── */}
      <main className="flex-1 flex flex-col md:flex-row gap-4 p-4 max-w-6xl mx-auto w-full md:overflow-hidden">

        {/* Left — Chat */}
        <section className="flex-1 flex flex-col min-h-[60vh] md:min-h-0">
          <ChatWindow
            messages={messages}
            setMessages={setMessages}
            setVerdict={setVerdict}
            setLoading={setLoading}
          />
        </section>

        {/* Right — Verdict + Actions + Trending */}
        <aside className="md:w-80 flex flex-col gap-4 overflow-y-auto pr-1">
          <VerdictCard verdict={verdict} loading={loading} />
          <ActionButtons verdict={verdict} />

          <div className="mt-4">
            <TrendingPanel campaigns={trendingCampaigns} />
          </div>
        </aside>

      </main>

    </div>
  )
}

export default App