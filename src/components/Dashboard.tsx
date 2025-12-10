import { useState, useEffect } from 'react';
import { loadCorrelations } from '../utils/dataLoader';
import type { CorrelationData } from '../utils/types';
import { Loader2 } from 'lucide-react';
import InsightCards from './InsightCards';
import ActivityTimeline from './ActivityTimeline';
import CorrelationGrid from './CorrelationGrid';

export default function Dashboard() {
  const [data, setData] = useState<CorrelationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const correlationData = await loadCorrelations();
        setData(correlationData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin" />
          <p className="text-slate-300 text-lg">Loading FlowState insights...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-400 mb-3">Failed to Load Data</h2>
          <p className="text-slate-300 mb-4">{error || 'Unknown error occurred'}</p>
          <p className="text-slate-400 text-sm">
            Make sure you ran Python scripts to generate the correlation data:
          </p>
          <pre className="mt-2 bg-slate-950 p-3 rounded text-xs text-slate-300 overflow-x-auto">
            python scripts/parse_youtube.py{'\n'}
            python scripts/fetch_github.py{'\n'}
            python scripts/correlate_data.py
          </pre>
        </div>
      </div>
    );
  }

  // Success state
  return (
    <div className="min-h-screen bg-slate-950 py-8 px-4 sm:px-8">
      <div className="max-w-[1400px] mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-4">
          <h1 className="text-5xl sm:text-6xl font-bold bg-gradient-to-r from-orange-500 via-red-500 to-green-500 bg-clip-text text-transparent">
            FlowState
          </h1>
          <p className="text-xl text-slate-300">
            The Science of Your Coding Flow
          </p>
          <div className="flex items-center justify-center gap-4 mt-4">
            <span className="px-4 py-2 bg-orange-500/20 border border-orange-500 rounded-full text-orange-400 text-sm font-medium">
              🎵 Music
            </span>
            <span className="px-4 py-2 bg-red-500/20 border border-red-500 rounded-full text-red-400 text-sm font-medium">
              📺 Videos
            </span>
            <span className="px-4 py-2 bg-green-500/20 border border-green-500 rounded-full text-green-400 text-sm font-medium">
              💻 Commits
            </span>
          </div>
        </header>

        {/* InsightCards */}
        <InsightCards insights={data.insights} />

        {/* CorrelationGrid */}
        <CorrelationGrid correlations={data.correlations} />

        {/* ActivityTimeline */}
        <ActivityTimeline data={data.timeline} />
      </div>
    </div>
  );
}
