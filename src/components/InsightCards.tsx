import { Headphones, Youtube, Zap, Target } from 'lucide-react';
import { Insights } from '../utils/types';

interface InsightCardsProps {
  insights: Insights;
}

export default function InsightCards({ insights }: InsightCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {/* Card 1: Music Impact */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-orange-500/20 hover:border-orange-500">
        <div className="flex items-center gap-3 mb-3">
          <Headphones className="w-6 h-6 text-orange-500" />
          <h3 className="text-lg font-semibold text-white">Music Impact</h3>
        </div>
        <p className="text-2xl font-bold text-orange-400">{insights.music_impact}</p>
        <p className="text-sm text-slate-400 mt-2">Background music boost</p>
      </div>

      {/* Card 2: Video Impact */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-red-500/20 hover:border-red-500">
        <div className="flex items-center gap-3 mb-3">
          <Youtube className="w-6 h-6 text-red-500" />
          <h3 className="text-lg font-semibold text-white">Video Impact</h3>
        </div>
        <p className="text-2xl font-bold text-red-400">{insights.video_impact}</p>
        <p className="text-sm text-slate-400 mt-2">Learning content boost</p>
      </div>

      {/* Card 3: Synergy Boost */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-green-500/20 hover:border-transparent hover:bg-gradient-to-br hover:from-orange-500/10 hover:via-red-500/10 hover:to-green-500/10">
        <div className="flex items-center gap-3 mb-3">
          <Zap className="w-6 h-6 bg-gradient-to-r from-orange-500 via-red-500 to-green-500 bg-clip-text text-transparent" />
          <h3 className="text-lg font-semibold text-white">Synergy Boost</h3>
        </div>
        <p className="text-2xl font-bold bg-gradient-to-r from-orange-400 via-red-400 to-green-400 bg-clip-text text-transparent">
          {insights.synergy_boost}
        </p>
        <p className="text-sm text-slate-400 mt-2">Combined music + videos</p>
      </div>

      {/* Card 4: Best Pattern */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-green-500/20 hover:border-green-500">
        <div className="flex items-center gap-3 mb-3">
          <Target className="w-6 h-6 text-green-500" />
          <h3 className="text-lg font-semibold text-white">Best Pattern</h3>
        </div>
        <p className="text-2xl font-bold text-green-400">{insights.best_pattern}</p>
        <p className="text-sm text-slate-400 mt-2">Optimal flow state</p>
      </div>
    </div>
  );
}
