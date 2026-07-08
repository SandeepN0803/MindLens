import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Activity } from 'lucide-react'

export default function EmotionChart({ emotions }) {
  // Format data for Recharts
  const data = emotions.map(e => ({
    name: e.label.charAt(0).toUpperCase() + e.label.slice(1),
    confidence: Math.round(e.confidence * 100)
  }))

  // Color mapping based on emotion
  const getEmotionColor = (label) => {
    switch (label.toLowerCase()) {
      case 'joy': return '#10b981' // emerald
      case 'sadness': return '#6366f1' // indigo
      case 'anger': return '#f43f5e' // rose
      case 'fear': return '#8b5cf6' // violet
      case 'disgust': return '#14b8a6' // teal
      case 'surprise': return '#f59e0b' // amber
      default: return '#64748b' // slate
    }
  }

  return (
    <div className="glass rounded-2xl p-6">
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
        <Activity size={18} className="text-indigo-400" />
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
              tick={{ fill: '#cbd5e1', fontSize: 14 }}
              width={80}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px', color: '#f1f5f9' }}
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
