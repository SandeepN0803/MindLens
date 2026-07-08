import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'

export default function JournalInput({ onAnalyzeSuccess }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, user_id: 'local_user' }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to analyze entry. The server might be down or processing too slowly.')
      }
      
      const data = await response.json()
      onAnalyzeSuccess(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass rounded-2xl p-6 flex flex-col relative overflow-hidden transition-all focus-within:ring-2 focus-within:ring-indigo-500/50">
      
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
          New Entry
        </h2>
        {/* We can add real-time language detection ping here later if needed */}
      </div>

      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="How are you feeling right now? What's on your mind? (Supports English, Hindi, Kannada, Telugu, Tamil)"
        className="w-full min-h-[200px] resize-y bg-transparent border-none focus:ring-0 text-slate-200 placeholder-slate-500 text-lg leading-relaxed outline-none"
      />

      <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-700/50">
        <span className="text-sm text-slate-500">
          {text.length} characters
        </span>
        <button
          onClick={handleAnalyze}
          disabled={loading || text.trim().length === 0}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all
            ${loading ? 'bg-indigo-600/50 text-indigo-200 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg hover:shadow-indigo-500/25'}
            disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Sparkles className="w-5 h-5" />
          )}
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-500/20 text-red-200 rounded-lg text-sm border border-red-500/30">
          {error}
        </div>
      )}
    </div>
  )
}
