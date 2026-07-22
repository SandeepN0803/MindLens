import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Activity } from 'lucide-react'

export default function EmotionChart({ emotions }) {
  if (!emotions || emotions.length === 0) return null
  
  if (emotions[0]?.error) {
    return (
      <div className="glass rounded-lg p-[20px] text-center text-error bg-error-container/10">
        <Activity className="w-10 h-10 mx-auto mb-3 opacity-50" />
        <p className="text-[16px]">Emotion analysis unavailable at this time.</p>
      </div>
    )
  }

  // Format data for Recharts
  const data = emotions.map(e => ({
    name: e.label.charAt(0).toUpperCase() + e.label.slice(1),
    confidence: Math.round(e.confidence * 100)
  }))

  // Color mapping based on new palette tokens
  const getEmotionColor = (label) => {
    switch (label.toLowerCase()) {
      case 'joy': return '#81b29a' // sentiment-positive
      case 'sadness': return '#b4b7ff' // primary
      case 'anger': return '#e07a5f' // sentiment-negative
      case 'fear': return '#e3badb' // tertiary
      case 'disgust': return '#c2c5dd' // secondary
      case 'surprise': return '#ffd7f4' // on-tertiary-container
      default: return '#94a3b8' // sentiment-neutral
    }
  }

  return (
    <div className="glass rounded-lg p-[20px]">
      <h3 className="text-[18px] font-semibold flex items-center gap-2 mb-6 text-on-surface">
        <Activity size={18} className="text-primary" />
        Detected Emotions
      </h3>
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 20, left: 20, bottom: 0 }}
          >
            <XAxis type="number" hide domain={[0, 100]} />
            <YAxis 
              type="category" 
              dataKey="name" 
              axisLine={false} 
              tickLine={false}
              tick={{ fill: '#c8c5d0', fontSize: 14 }}
              width={80}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: '#1f1f23', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#e4e1e6' }}
              formatter={(value) => [`${value}%`, 'Confidence']}
            />
            <Bar dataKey="confidence" radius={[0, 4, 4, 0]} barSize={24}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getEmotionColor(entry.name)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
