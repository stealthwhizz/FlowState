import type { Correlations } from '../utils/types';

interface CorrelationGridProps {
  correlations: Correlations;
}

export default function CorrelationGrid({ correlations }: CorrelationGridProps) {
  // Calculate baseline (neither) for percentage calculations
  const baseline = correlations.neither.avg_commits;
  
  const calculateBoost = (value: number): string => {
    if (baseline === 0) return '+0%';
    const boost = ((value - baseline) / baseline) * 100;
    return `${boost >= 0 ? '+' : ''}${boost.toFixed(1)}%`;
  };

  const gridItems = [
    {
      title: 'Music Only',
      subtitle: 'Background focus',
      value: correlations.music_only.avg_commits,
      days: correlations.music_only.days,
      boost: calculateBoost(correlations.music_only.avg_commits),
      color: 'orange',
      bgClass: 'bg-orange-500/10 border-orange-500/30 hover:border-orange-500/50',
      textClass: 'text-orange-400',
      glowClass: 'hover:shadow-orange-500/20'
    },
    {
      title: 'Videos Only',
      subtitle: 'Learning content',
      value: correlations.video_only.avg_commits,
      days: correlations.video_only.days,
      boost: calculateBoost(correlations.video_only.avg_commits),
      color: 'red',
      bgClass: 'bg-red-500/10 border-red-500/30 hover:border-red-500/50',
      textClass: 'text-red-400',
      glowClass: 'hover:shadow-red-500/20'
    },
    {
      title: 'Neither',
      subtitle: 'Baseline productivity',
      value: correlations.neither.avg_commits,
      days: correlations.neither.days,
      boost: '0%',
      color: 'slate',
      bgClass: 'bg-slate-700/30 border-slate-600/30 hover:border-slate-500/50',
      textClass: 'text-slate-400',
      glowClass: 'hover:shadow-slate-500/20'
    },
    {
      title: 'Both',
      subtitle: 'Optimal flow state',
      value: correlations.both.avg_commits,
      days: correlations.both.days,
      boost: calculateBoost(correlations.both.avg_commits),
      color: 'gradient',
      bgClass: 'bg-gradient-to-br from-orange-500/10 via-red-500/10 to-green-500/10 border-2 border-transparent bg-gradient-to-r from-orange-500 via-red-500 to-green-500 bg-clip-border hover:from-orange-400 hover:via-red-400 hover:to-green-400',
      textClass: 'text-green-400',
      glowClass: 'hover:shadow-green-500/20'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">Correlation Matrix</h2>
        <p className="text-slate-400">How different consumption patterns affect coding productivity</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {gridItems.map((item) => (
          <div
            key={item.title}
            className={`
              relative p-6 rounded-xl border transition-all duration-300 
              transform hover:scale-105 hover:shadow-2xl cursor-pointer
              ${item.bgClass} ${item.glowClass}
            `}
          >
            {/* Gradient border for "Both" cell */}
            {item.color === 'gradient' && (
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-orange-500 via-red-500 to-green-500 p-[2px]">
                <div className="h-full w-full rounded-xl bg-slate-900/90 backdrop-blur-sm" />
              </div>
            )}
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                <span className={`text-sm font-medium ${item.textClass}`}>
                  {item.boost}
                </span>
              </div>
              
              <p className="text-slate-400 text-sm mb-4">{item.subtitle}</p>
              
              <div className="space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className={`text-3xl font-bold ${item.textClass}`}>
                    {item.value.toFixed(1)}
                  </span>
                  <span className="text-slate-400 text-sm">avg commits</span>
                </div>
                
                <div className="text-slate-500 text-xs">
                  {item.days} days sampled
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center text-slate-400 text-sm max-w-2xl mx-auto">
        <p>
          Each cell shows the average commits per day for different consumption patterns. 
          The "Both" pattern represents the optimal flow state combining music focus with video learning.
        </p>
      </div>
    </div>
  );
}