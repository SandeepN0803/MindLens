import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { TrendingUp } from 'lucide-react'

export default function MoodTimeline({ entries }) {
  if (!entries || entries.length === 0) {
    return null
  }

  // Transform entries into time-series data
  // We map sentiments to a numerical score for the timeline: 
  // Positive = 1, Neutral = 0, Negative = -1
  const data = entries.map(entry => {
    let score = 0
    if (entry.sentiment.label === 'positive') score = 1
    else if (entry.sentiment.label === 'negative') score = -1
    
    // Format timestamp
    const date = new Date(entry.timestamp)
    const formattedDate = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    
    return {
      date: formattedDate,
      score,
      originalDate: date // keep for sorting
    }
  }).sort((a, b) => a.originalDate - b.originalDate)

  return (
    <div className="glass rounded-2xl p-6">
      <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
        <TrendingUp size={18} className="text-indigo-400" />
        Mood Trend
      </h3>
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis 
              dataKey="date" 
              axisLine={false} 
              tickLine={false}
              tick={{ fill: '#cbd5e1', fontSize: 12 }}
              dy={10}
            />
            <YAxis 
              domain={[-1.2, 1.2]}
              ticks={[-1, 0, 1]}
              axisLine={false}
              tickLine={false}
              tickFormatter={(val) => {
                if (val === 1) return 'Positive'
                if (val === 0) return 'Neutral'
                if (val === -1) return 'Negative'
                return ''
              }}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f1f5f9' }}
              labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
              formatter={(value) => {
                if (value > 0) return ['Positive', 'Mood']
                if (value < 0) return ['Negative', 'Mood']
                return ['Neutral', 'Mood']
              }}
            />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#818cf8" 
              strokeWidth={3}
              dot={{ fill: '#818cf8', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: '#6366f1' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
