import { MessageSquare, Globe2 } from 'lucide-react'

export default function ResultCard({ result }) {
  const { sentiment, detected_language, language_confidence } = result
  
  // Refined Color Palette
  const sentimentConfig = {
    positive: {
      color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      label: 'Positive Moment',
      bar: 'bg-emerald-500'
    },
    neutral: {
      color: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
      label: 'Balanced/Neutral',
      bar: 'bg-slate-500'
    },
    negative: {
      color: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      label: 'Noticed a difficult moment',
      bar: 'bg-orange-500'
    },
    error: {
      color: 'bg-red-500/20 text-red-400 border-red-500/30',
      label: 'Analysis unavailable',
      bar: 'bg-red-500'
    }
  }

  const config = sentiment.error ? sentimentConfig.error : (sentimentConfig[sentiment.label] || sentimentConfig.neutral)

  return (
    <div className="glass rounded-2xl p-6 flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare size={18} className="text-indigo-400" />
          Analysis Overview
        </h3>
        <div className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-400">
          <Globe2 size={12} />
          Language: {detected_language} ({Math.round(language_confidence * 100)}%)
        </div>
      </div>
      
      <div className={`p-4 rounded-xl border flex flex-col gap-3 ${config.color}`}>
        <div className="flex justify-between items-end">
          <span className="font-medium text-lg">{config.label}</span>
          <span className="text-sm opacity-80">{Math.round(sentiment.confidence * 100)}% Confidence</span>
        </div>
        
        {/* Progress Bar */}
        {!sentiment.error && (
          <div className="h-2 w-full bg-slate-900/50 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ease-out ${config.bar}`}
              style={{ width: `${sentiment.confidence * 100}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
