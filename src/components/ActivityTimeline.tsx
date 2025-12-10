import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TimelineDataPoint } from '../utils/types';

interface ActivityTimelineProps {
  data: TimelineDataPoint[];
}

export default function ActivityTimeline({ data }: ActivityTimelineProps) {
  // Filter to last 3.5 months (105 days)
  const filterToLast105Days = (data: TimelineDataPoint[]): TimelineDataPoint[] => {
    if (data.length === 0) return [];
    
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const latestDate = new Date(sortedData[sortedData.length - 1].date);
    const cutoffDate = new Date(latestDate);
    cutoffDate.setDate(cutoffDate.getDate() - 105);
    
    return sortedData.filter(point => new Date(point.date) >= cutoffDate);
  };

  const filteredData = filterToLast105Days(data);

  // Custom tooltip with dark background and colored values for three sources
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-lg">
          <p className="text-slate-300 text-sm mb-2">{payload[0].payload.date}</p>
          <p className="text-orange-400 text-sm">
            Music Sessions: <span className="font-semibold">{payload[0].payload.music_count}</span>
          </p>
          <p className="text-red-400 text-sm">
            Videos Watched: <span className="font-semibold">{payload[0].payload.video_count}</span>
          </p>
          <p className="text-green-400 text-sm">
            GitHub Commits: <span className="font-semibold">{payload[0].payload.commit_count}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-orange-400 via-red-400 to-green-400 bg-clip-text text-transparent">
        Three-Source Activity Timeline
      </h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={filteredData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="date" 
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis 
            yAxisId="left" 
            stroke="#f97316"
            tick={{ fill: '#f97316' }}
            label={{ value: 'Music & Videos', angle: -90, position: 'insideLeft', fill: '#f97316' }}
          />
          <YAxis 
            yAxisId="right" 
            orientation="right"
            stroke="#10b981"
            tick={{ fill: '#10b981' }}
            label={{ value: 'GitHub Commits', angle: 90, position: 'insideRight', fill: '#10b981' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="music_count" 
            stroke="#f97316" 
            strokeWidth={2}
            dot={{ fill: '#f97316', r: 3 }}
            activeDot={{ r: 5 }}
            name="Music Sessions"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="video_count" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={{ fill: '#ef4444', r: 3 }}
            activeDot={{ r: 5 }}
            name="Videos Watched"
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="commit_count" 
            stroke="#10b981" 
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 3 }}
            activeDot={{ r: 5 }}
            name="GitHub Commits"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
