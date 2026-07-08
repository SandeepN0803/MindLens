import { useState, useEffect } from 'react'
import JournalInput from './components/JournalInput'
import ResultCard from './components/ResultCard'
import EmotionChart from './components/EmotionChart'
import ThoughtPatterns from './components/ThoughtPatterns'
import MoodTimeline from './components/MoodTimeline'
import PatternHeatmap from './components/PatternHeatmap'
import { Book, LineChart, History } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('journal')
  const [currentResult, setCurrentResult] = useState(null)
  
  // Lifted state to keep history across tabs (fetched from backend)
  const [entries, setEntries] = useState([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await fetch('/api/history')
        if (response.ok) {
          const data = await response.json()
          setEntries(data)
        }
      } catch (err) {
        console.error("Failed to fetch history:", err)
      } finally {
        setIsLoadingHistory(false)
      }
    }
    fetchHistory()
  }, [])

  const handleAnalyzeSuccess = (result) => {
    setCurrentResult(result)
    setEntries(prev => [result, ...prev])
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center py-10 px-4 md:px-8">
      
      {/* Header */}
      <header className="max-w-4xl w-full flex flex-col items-center mb-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400 tracking-tight mb-2">
          MindLens
        </h1>
        <p className="text-slate-400 max-w-lg">
          Your multilingual mental health journal. Write your thoughts safely, and let AI help you find perspective.
        </p>
      </header>

      {/* Tabs */}
      <div className="flex bg-slate-800/50 p-1 rounded-2xl mb-8 border border-slate-700/50">
        <button 
          onClick={() => setActiveTab('journal')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all ${activeTab === 'journal' ? 'bg-indigo-500/20 text-indigo-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <Book size={18} />
          Journal
        </button>
        <button 
          onClick={() => setActiveTab('history')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all ${activeTab === 'history' ? 'bg-indigo-500/20 text-indigo-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <History size={18} />
          History
        </button>
        <button 
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all ${activeTab === 'analytics' ? 'bg-indigo-500/20 text-indigo-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
        >
          <LineChart size={18} />
          Analytics
        </button>
      </div>

      {/* Main Content Area */}
      <main className="max-w-4xl w-full flex flex-col gap-6">
        
        {activeTab === 'journal' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            
            {/* Left Column: Input */}
            <div className="flex flex-col gap-4">
              <JournalInput onAnalyzeSuccess={handleAnalyzeSuccess} />
            </div>

            {/* Right Column: Results (if any) */}
            <div className="flex flex-col gap-4">
              {currentResult ? (
                <>
                  <ResultCard result={currentResult} />
                  
                  {currentResult.emotions && currentResult.emotions.length > 0 && (
                    <EmotionChart emotions={currentResult.emotions} />
                  )}
                  
                  <ThoughtPatterns 
                    distortions={currentResult.distortions} 
                    reframings={currentResult.reframings} 
                  />
                </>
              ) : (
                <div className="glass rounded-2xl p-8 flex flex-col items-center justify-center text-center h-full min-h-[300px] text-slate-500">
                  <Book className="w-12 h-12 mb-4 opacity-50" />
                  <p>Write an entry to see your personalized analysis here.</p>
                </div>
              )}
            </div>

          </div>
        )}

        {activeTab === 'history' && (
          <div className="flex flex-col gap-4">
            {isLoadingHistory ? (
              <div className="glass rounded-2xl p-8 text-center text-slate-400">Loading history...</div>
            ) : entries.length === 0 ? (
              <div className="glass rounded-2xl p-8 text-center text-slate-400">
                No entries yet. Head to the Journal tab to write your first!
              </div>
            ) : (
              entries.map((entry, idx) => (
                <div key={entry.entry_id || idx} className="glass rounded-2xl p-6">
                  <div className="text-sm text-slate-500 mb-2">
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                  <p className="text-slate-200 mb-4 whitespace-pre-wrap">{entry.input_text}</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ResultCard result={entry} />
                    <ThoughtPatterns distortions={entry.distortions} reframings={entry.reframings} />
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="flex flex-col gap-6">
            {isLoadingHistory ? (
              <div className="glass rounded-2xl p-8 text-center text-slate-400">Loading analytics...</div>
            ) : entries.length === 0 ? (
              <div className="glass rounded-2xl p-8 text-center text-slate-400">
                Not enough data for analytics. Start journaling to see your trends!
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                <MoodTimeline entries={entries} />
                <PatternHeatmap entries={entries} />
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  )
}

export default App
