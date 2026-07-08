import { useState } from 'react'
import { BrainCircuit, ChevronDown, Sparkles } from 'lucide-react'

export default function ThoughtPatterns({ distortions, reframings }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!distortions || distortions.length === 0) {
    return (
      <div className="glass rounded-2xl p-6 text-center text-slate-400">
        <BrainCircuit className="w-10 h-10 mx-auto mb-3 opacity-30" />
        <p>No notable thought patterns detected in this entry.</p>
      </div>
    )
  }

  const handleToggle = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <div className="glass rounded-2xl p-6">
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
        <BrainCircuit size={18} className="text-indigo-400" />
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
              className={`border transition-all duration-300 rounded-xl overflow-hidden ${
                isExpanded ? 'bg-slate-800/80 border-indigo-500/50' : 'bg-slate-800/40 border-slate-700 hover:border-slate-600 cursor-pointer'
              }`}
            >
              <div 
                className="p-4 flex items-center justify-between"
                onClick={() => !isExpanded && handleToggle(index)}
              >
                <div className="flex flex-col">
                  <span className="font-medium text-slate-200 group relative">
                    A thought pattern I noticed...
                    <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-400">
                      {dist.label}
                    </span>
                  </span>
                </div>
                
                <button 
                  onClick={(e) => { e.stopPropagation(); handleToggle(index) }}
                  className="p-1 rounded-full hover:bg-slate-700 text-slate-400"
                >
                  <ChevronDown className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </button>
              </div>
              
              {/* Expandable Reframing Section */}
              <div 
                className={`transition-all duration-300 ease-in-out ${
                  isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="p-4 pt-0 border-t border-slate-700/50 bg-slate-800/50 mt-2">
                  <div className="mt-4 flex gap-3">
                    <Sparkles className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-indigo-300 mb-1">New Perspective</h4>
                      <p className="text-slate-300 text-sm leading-relaxed">
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
