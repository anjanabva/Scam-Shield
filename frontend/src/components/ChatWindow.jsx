import React, { useState, useRef, useEffect } from 'react'
import { analyze, followupStream } from '../api/client'

/**
 * ChatWindow
 *
 * Props:
 *   messages    {Array<{role:'user'|'assistant', text:string}>}
 *   setMessages {Function}
 *   setVerdict  {Function}   – called with the analysis result object
 *   setLoading  {Function}
 */
const ChatWindow = ({ messages, setMessages, setVerdict, setLoading }) => {
  const [input, setInput] = useState('')
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  // Track the original transcript so follow-up calls have context
  const transcriptRef = useRef('')

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const isFirstMessage = messages.length === 0

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return

    setError(null)
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])

    try {
      setLoading(true)

      if (isFirstMessage) {
        // First message → full analysis
        transcriptRef.current = text
        const result = await analyze(text)
        setVerdict(result)
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            text: result.explanation || 'Analysis complete — see the verdict panel →',
          },
        ])
      } else {
        // Subsequent messages → follow-up stream
        setMessages(prev => [...prev, { role: 'assistant', text: '' }])
        
        await followupStream(text, transcriptRef.current, messages, (chunk) => {
          setMessages(prev => {
            const newMessages = [...prev]
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              text: newMessages[newMessages.length - 1].text + chunk
            }
            return newMessages
          })
        })
      }
    } catch (err) {
      setError(err.message)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: '⚠️ Could not reach the backend. Make sure the FastAPI server is running.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col flex-1 rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">

      {/* ── Message list ── */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center py-12">
            <span className="text-5xl">🛡️</span>
            <p className="text-gray-400 text-sm max-w-xs leading-relaxed">
              Paste a call transcript, WhatsApp message, or suspicious email below.
              <br />
              <span className="text-indigo-400 font-medium">Get a verdict in seconds.</span>
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
                ${msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-sm'
                  : 'bg-gray-800 text-gray-100 rounded-bl-sm border border-gray-700'
                }
              `}
            >
              {msg.text}
            </div>
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="mx-4 mb-2 px-3 py-2 rounded-lg bg-red-900/40 border border-red-700 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* ── Input area ── */}
      <div className="border-t border-gray-800 p-3 flex gap-2 items-end">
        <textarea
          id="chat-input"
          rows={3}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={
            isFirstMessage
              ? 'Paste a call transcript, SMS, or email here…'
              : 'Ask a follow-up question…'
          }
          className="
            flex-1 resize-none rounded-xl bg-gray-800 border border-gray-700
            text-gray-100 placeholder-gray-500 text-sm px-4 py-3
            focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
            transition-colors
          "
        />
        <button
          id="send-btn"
          onClick={sendMessage}
          disabled={!input.trim()}
          className="
            flex-shrink-0 h-10 w-10 rounded-xl bg-indigo-600 hover:bg-indigo-500
            disabled:opacity-30 disabled:cursor-not-allowed
            flex items-center justify-center transition-all duration-150
            hover:scale-105 active:scale-95
          "
          aria-label="Send"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-white">
            <path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405Z" />
          </svg>
        </button>
      </div>

    </div>
  )
}

export default ChatWindow