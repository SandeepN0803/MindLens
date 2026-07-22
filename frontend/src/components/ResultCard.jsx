import { MessageSquare, Globe2 } from 'lucide-react'

export default function ResultCard({ result }) {
  const { sentiment, detected_language, language_confidence } = result
  
  // Refined Color Palette
  const sentimentConfig = {
    positive: {
      color: 'bg-sentiment-positive/10 text-sentiment-positive border-sentiment-positive/30',
      label: 'Positive Moment',
      bar: 'bg-sentiment-positive'
    },
    neutral: {
      color: 'bg-sentiment-neutral/10 text-sentiment-neutral border-sentiment-neutral/30',
      label: 'Balanced/Neutral',
      bar: 'bg-sentiment-neutral'
    },
    negative: {
      color: 'bg-sentiment-negative/10 text-sentiment-negative border-sentiment-negative/30',
      label: 'Noticed a difficult moment',
      bar: 'bg-sentiment-negative'
    },
    error: {
      color: 'bg-error-container text-on-error-container border-error/30',
      label: 'Analysis unavailable',
      bar: 'bg-error'
    }
  }

  const config = sentiment.error ? sentimentConfig.error : (sentimentConfig[sentiment.label] || sentimentConfig.neutral)

  return (
    <div className="glass rounded-lg p-[20px] flex flex-col gap-[12px]">
      <div className="flex justify-between items-start">
        <h3 className="text-[18px] font-semibold flex items-center gap-2 text-on-surface">
          <MessageSquare size={18} className="text-primary" />
          Analysis Overview
        </h3>
        <div className="flex items-center gap-[6px] text-[12px] font-medium px-3 py-1 rounded-full bg-surface-container border border-outline-variant/30 text-on-surface-variant">
          <Globe2 size={12} />
          Language: {detected_language} ({Math.round(language_confidence * 100)}%)
        </div>
      </div>
      
      <div className={`p-4 rounded-md border flex flex-col gap-3 ${config.color}`}>
        <div className="flex justify-between items-end">
          <span className="font-medium text-[16px]">{config.label}</span>
          <span className="text-[12px] opacity-80">{Math.round(sentiment.confidence * 100)}% Confidence</span>
        </div>
        
        {/* Progress Bar */}
        {!sentiment.error && (
          <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden">
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
