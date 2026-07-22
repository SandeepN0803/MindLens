import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'

export default function JournalInput({ onAnalyzeSuccess, onLoadingChange }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (loading || !text.trim()) return
    setLoading(true)
    if (onLoadingChange) onLoadingChange(true)
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
      if (onLoadingChange) onLoadingChange(false)
    }
  }

  return (
    <div className="glass rounded-lg p-[20px] flex flex-col relative overflow-hidden transition-all focus-within:ring-2 focus-within:ring-primary/50">
      
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-[22px] font-medium text-on-surface flex items-center gap-2 leading-title">
          New Entry
        </h2>
        {/* We can add real-time language detection ping here later if needed */}
      </div>

      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="How are you feeling right now? What's on your mind? (Supports English, Hindi, Kannada, Telugu, Tamil)"
        className="w-full min-h-[200px] resize-y bg-transparent border-none focus:ring-0 text-on-surface placeholder-outline-variant text-[16px] leading-body outline-none"
      />

      <div className="flex items-center justify-between mt-6 pt-4 border-t border-outline-variant/30">
        <span className="text-[12px] font-medium text-on-surface-variant">
          {text.length} characters
        </span>
        <button
          onClick={handleAnalyze}
          disabled={loading || text.trim().length === 0}
          className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all
            ${loading ? 'bg-primary-container text-on-primary-container cursor-wait' : 'bg-primary hover:opacity-90 text-on-primary shadow-sm'}
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
        <div className="mt-4 p-3 bg-error-container text-on-error-container rounded-md text-[12px] font-medium border border-error/30" aria-live="assertive">
          {error}
        </div>
      )}
    </div>
  )
}
