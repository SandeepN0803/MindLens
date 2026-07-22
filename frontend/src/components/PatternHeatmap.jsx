import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { LayoutGrid } from 'lucide-react'

export default function PatternHeatmap({ entries }) {
  if (!entries || entries.length === 0) {
    return null
  }

  // Count frequencies of each distortion
  const counts = {}
  entries.forEach(entry => {
    if (entry.distortions) {
      entry.distortions.forEach(dist => {
        counts[dist.label] = (counts[dist.label] || 0) + 1
      })
    }
  })

  // Format data for Recharts, sort by frequency descending
  const data = Object.keys(counts)
    .map(label => ({
      name: label,
      count: counts[label]
    }))
    .sort((a, b) => b.count - a.count)

  if (data.length === 0) {
    return (
      <div className="glass rounded-lg p-[20px] text-center text-on-surface-variant flex flex-col items-center justify-center h-full min-h-[200px]">
        <LayoutGrid className="w-8 h-8 mb-3 opacity-30" />
        <p className="text-[16px]">No thought patterns detected in your history yet.</p>
      </div>
    )
  }

  return (
    <div className="glass rounded-lg p-[20px]">
      <h3 className="text-[18px] font-semibold flex items-center gap-2 mb-6 text-on-surface">
        <LayoutGrid size={18} className="text-primary" />
        Frequent Thought Patterns
      </h3>
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
          >
            <XAxis type="number" hide />
            <YAxis 
              type="category" 
              dataKey="name" 
              axisLine={false} 
              tickLine={false}
              tick={{ fill: '#c8c5d0', fontSize: 12 }}
              width={110}
            />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: '#1f1f23', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#e4e1e6' }}
              formatter={(value) => [value, 'Occurrences']}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill="#b4b7ff" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
