import { useState } from 'react'
import { BrainCircuit, ChevronDown, Sparkles } from 'lucide-react'

export default function ThoughtPatterns({ distortions, reframings }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!distortions || distortions.length === 0) {
    return (
      <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant">
        <BrainCircuit className="w-10 h-10 mx-auto mb-3 opacity-30" />
        <p className="text-[16px]">No notable thought patterns detected in this entry.</p>
      </div>
    )
  }

  if (distortions[0]?.error) {
    return (
      <div className="glass rounded-lg p-[20px] text-center text-error bg-error-container/10">
        <BrainCircuit className="w-10 h-10 mx-auto mb-3 opacity-50" />
        <p className="text-[16px]">Pattern analysis unavailable at this time.</p>
      </div>
    )
  }

  const handleToggle = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <div className="glass rounded-lg p-[20px]">
      <h3 className="text-[18px] font-semibold flex items-center gap-2 mb-4 text-on-surface">
        <BrainCircuit size={18} className="text-primary" />
        Thought Patterns
      </h3>
      
      <div className="flex flex-col gap-3">
        {distortions.map((dist, index) => {
          // Find matching reframing if it exists
          const reframing = reframings?.find(r => r.distortion === dist.label)
          const isExpanded = expandedIndex === index
          
          return (
            <div 
              key={index}
              className={`border transition-all duration-300 rounded-md overflow-hidden ${
                isExpanded ? 'bg-surface-container-high border-primary/50' : 'bg-surface-container border-outline-variant/30 hover:border-outline-variant cursor-pointer'
              }`}
            >
              <div 
                className="p-4 flex items-center justify-between"
                onClick={() => !isExpanded && handleToggle(index)}
              >
                <div className="flex flex-col">
                  <span className="font-medium text-[16px] text-on-surface group relative">
                    A thought pattern I noticed...
                    <span className="ml-2 text-[12px] px-2 py-0.5 rounded-full bg-surface-container-highest text-on-surface-variant font-medium">
                      {dist.label}
                    </span>
                  </span>
                </div>
                
                <button 
                  onClick={(e) => { e.stopPropagation(); handleToggle(index) }}
                  className="p-1 rounded-full hover:bg-surface-container-highest text-on-surface-variant transition-colors"
                >
                  <ChevronDown className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </button>
              </div>
              
              <div 
                className={`transition-all duration-300 ease-in-out ${
                  isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="p-4 pt-0 border-t border-outline-variant/30 bg-surface-container-high mt-2">
                  <div className="mt-4 flex gap-3">
                    <Sparkles className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-[14px] font-medium text-primary mb-1">New Perspective</h4>
                      <p className="text-on-surface-variant text-[14px] leading-body">
                        {reframing ? reframing.reframed : "Consider looking at this from a more balanced perspective."}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
