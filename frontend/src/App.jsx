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
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  
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
    <div className="min-h-screen bg-surface text-on-surface flex flex-col items-center pb-32 md:pb-10 px-4 md:px-8 font-sans">
      
      {/* TopAppBar */}
      <header className="max-w-4xl w-full flex items-center justify-center py-6 mb-4 md:mb-10">
        <h1 className="text-[32px] md:text-[57px] font-bold text-primary tracking-tight leading-tight">
          MindLens
        </h1>
      </header>

      {/* Desktop Navigation (Hidden on mobile) */}
      <div className="hidden md:flex bg-surface-container-low p-1 rounded-xl mb-8 border border-outline-variant/30 shadow-sm">
        <button 
          onClick={() => setActiveTab('journal')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'journal' ? 'bg-primary-container text-on-primary-container shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
        >
          <Book size={18} />
          Journal
        </button>
        <button 
          onClick={() => setActiveTab('history')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'history' ? 'bg-primary-container text-on-primary-container shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
        >
          <History size={18} />
          History
        </button>
        <button 
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'analytics' ? 'bg-primary-container text-on-primary-container shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}
        >
          <LineChart size={18} />
          Analytics
        </button>
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 w-full z-[100] glass border-t border-outline-variant/30 rounded-t-xl px-2 pb-6 pt-3 flex justify-around items-center">
        <button 
          onClick={() => setActiveTab('journal')}
          className={`flex flex-col items-center gap-1 p-2 w-20 transition-all ${activeTab === 'journal' ? 'text-primary' : 'text-on-surface-variant'}`}
        >
          <div className={`p-1.5 rounded-full ${activeTab === 'journal' ? 'bg-primary-container' : 'transparent'}`}>
            <Book size={20} className={activeTab === 'journal' ? 'text-on-primary-container' : ''} />
          </div>
          <span className="text-[10px] font-medium">Journal</span>
        </button>
        <button 
          onClick={() => setActiveTab('history')}
          className={`flex flex-col items-center gap-1 p-2 w-20 transition-all ${activeTab === 'history' ? 'text-primary' : 'text-on-surface-variant'}`}
        >
          <div className={`p-1.5 rounded-full ${activeTab === 'history' ? 'bg-primary-container' : 'transparent'}`}>
            <History size={20} className={activeTab === 'history' ? 'text-on-primary-container' : ''} />
          </div>
          <span className="text-[10px] font-medium">History</span>
        </button>
        <button 
          onClick={() => setActiveTab('analytics')}
          className={`flex flex-col items-center gap-1 p-2 w-20 transition-all ${activeTab === 'analytics' ? 'text-primary' : 'text-on-surface-variant'}`}
        >
          <div className={`p-1.5 rounded-full ${activeTab === 'analytics' ? 'bg-primary-container' : 'transparent'}`}>
            <LineChart size={20} className={activeTab === 'analytics' ? 'text-on-primary-container' : ''} />
          </div>
          <span className="text-[10px] font-medium">Analytics</span>
        </button>
      </div>

      {/* Main Content Area */}
      <main className="max-w-4xl w-full flex flex-col gap-[32px]">
        
        {activeTab === 'journal' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            
            {/* Left Column: Input */}
            <div className="flex flex-col gap-4">
              <JournalInput 
                onAnalyzeSuccess={handleAnalyzeSuccess} 
                onLoadingChange={setIsAnalyzing}
              />
            </div>

            {/* Right Column: Results (if any) */}
            <div className="flex flex-col gap-[12px]" aria-live="polite" aria-busy={isAnalyzing}>
              {isAnalyzing ? (
                <div className="glass rounded-lg p-[20px] flex flex-col gap-6 w-full animate-pulse min-h-[300px]">
                  <div className="h-6 bg-surface-container-highest rounded-sm w-1/3 mb-2"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-surface-container-high rounded-sm w-full"></div>
                    <div className="h-4 bg-surface-container-high rounded-sm w-5/6"></div>
                    <div className="h-4 bg-surface-container-high rounded-sm w-4/6"></div>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-[12px]">
                    <div className="h-20 bg-surface-container-high rounded-md"></div>
                    <div className="h-20 bg-surface-container-high rounded-md"></div>
                  </div>
                </div>
              ) : currentResult ? (
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
                <div className="glass rounded-lg p-[20px] flex flex-col items-center justify-center text-center h-full min-h-[300px] text-on-surface-variant">
                  <Book className="w-12 h-12 mb-4 opacity-30 text-primary" />
                  <p className="text-[16px]">Write an entry to see your personalized analysis here.</p>
                </div>
              )}
            </div>

          </div>
        )}

        {activeTab === 'history' && (
          <div className="flex flex-col gap-[12px]">
            {isLoadingHistory ? (
              <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant">Loading history...</div>
            ) : entries.length === 0 ? (
              <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant">
                No entries yet. Head to the Journal tab to write your first!
              </div>
            ) : (
              entries.map((entry, idx) => (
                <div key={entry.entry_id || idx} className="glass rounded-lg p-[20px]">
                  <div className="text-[12px] text-on-surface-variant mb-2 font-medium tracking-wide uppercase">
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                  <p className="text-[16px] text-on-surface mb-4 whitespace-pre-wrap">{entry.input_text}</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-[12px]">
                    <ResultCard result={entry} />
                    <ThoughtPatterns distortions={entry.distortions} reframings={entry.reframings} />
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="flex flex-col gap-[32px]">
            {isLoadingHistory ? (
              <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant">Loading analytics...</div>
            ) : entries.length === 0 ? (
              <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant">
                Not enough data for analytics. Start journaling to see your trends!
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-[32px] items-start">
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
