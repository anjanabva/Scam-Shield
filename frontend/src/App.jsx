import React, { useState } from 'react'

// Components will be built separately — import when ready
// import ChatWindow from './components/ChatWindow'
// import VerdictCard from './components/VerdictCard'
// import ActionButtons from './components/ActionButtons'

const App = () => {
  // Shared state — passed down as props to child components
  const [messages, setMessages] = useState([])       // chat history
  const [verdict, setVerdict] = useState(null)       // { verdict, confidence, red_flags, matched_pattern, explanation }
  const [loading, setLoading] = useState(false)      // API in-flight

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">

      {/* ── Header ── */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">🛡️</span>
        <h1 className="text-xl font-bold tracking-tight">Scam Shield</h1>
        <span className="text-xs text-gray-400 ml-auto">AI-Powered Fraud Detection</span>
      </header>

      {/* ── Main layout ── */}
      <main className="flex-1 flex flex-col md:flex-row gap-4 p-4 max-w-6xl mx-auto w-full">

        {/* Left — Chat area */}
        <section className="flex-1 flex flex-col gap-4">
          {/* ChatWindow goes here */}
          {/* <ChatWindow messages={messages} setMessages={setMessages} setVerdict={setVerdict} setLoading={setLoading} /> */}
          <div className="flex-1 rounded-xl border border-gray-800 bg-gray-900 p-4 text-gray-500 italic">
            ChatWindow — to be built
          </div>
        </section>

        {/* Right — Verdict + Actions */}
        <aside className="md:w-80 flex flex-col gap-4">
          {/* VerdictCard goes here */}
          {/* <VerdictCard verdict={verdict} loading={loading} /> */}
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-4 text-gray-500 italic">
            VerdictCard — to be built
          </div>

          {/* ActionButtons goes here */}
          {/* <ActionButtons verdict={verdict} /> */}
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-4 text-gray-500 italic">
            ActionButtons — to be built
          </div>
        </aside>

      </main>

    </div>
  )
}

export default App