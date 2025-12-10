export interface TimelineDataPoint {
  date: string;
  music_count: number;
  video_count: number;
  commit_count: number;
}

export interface Totals {
  total_music: number;
  total_videos: number;
  total_commits: number;
}

export interface CorrelationPattern {
  avg_commits: number;
  days: number;
}

export interface Correlations {
  music_only: CorrelationPattern;
  video_only: CorrelationPattern;
  both: CorrelationPattern;
  neither: CorrelationPattern;
}

export interface Insights {
  music_impact: string;
  video_impact: string;
  synergy_boost: string;
  best_pattern: string;
}

export interface CorrelationData {
  timeline: TimelineDataPoint[];
  totals: Totals;
  correlations: Correlations;
  insights: Insights;
}
