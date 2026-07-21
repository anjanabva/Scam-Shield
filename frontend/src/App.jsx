import React, { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import VerdictCard from './components/VerdictCard'
import ActionButtons from './components/ActionButtons'

const App = () => {
  // Shared state passed down as props
  const [messages, setMessages] = useState([])      // chat history
  const [verdict, setVerdict] = useState(null)      // { verdict, confidence, red_flags, matched_pattern, explanation }
  const [loading, setLoading] = useState(false)     // API in-flight

  const handleReset = () => {
    setMessages([])
    setVerdict(null)
    setLoading(false)
  }

  return (
    <div className="min-h-screen md:h-screen md:overflow-hidden bg-gray-950 text-white flex flex-col">

      {/* ── Header ── */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">🛡️</span>
        <div>
          <h1 className="text-lg font-bold tracking-tight leading-none">Scam Shield</h1>
          <p className="text-xs text-gray-500">AI-Powered Fraud Detection</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {verdict && (
            <button
              id="btn-reset"
              onClick={handleReset}
              className="text-xs text-gray-500 hover:text-gray-300 transition-colors px-3 py-1.5 rounded-lg border border-gray-700 hover:border-gray-500"
            >
              ↺ New analysis
            </button>
          )}
          <span className="text-xs text-gray-600 hidden sm:block">ET AI Hackathon 2026</span>
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

        {/* Right — Verdict + Actions */}
        <aside className="md:w-80 flex flex-col gap-4">
          <VerdictCard verdict={verdict} loading={loading} />
          <ActionButtons verdict={verdict} />
        </aside>

      </main>

    </div>
  )
}

export default App