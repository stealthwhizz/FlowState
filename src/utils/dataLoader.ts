import type { CorrelationData } from './types';

export function validateCorrelationData(data: any): data is CorrelationData {
  // Check top-level structure
  if (!data || typeof data !== 'object') {
    throw new Error('Correlation data must be an object');
  }

  // Check timeline array
  if (!Array.isArray(data.timeline)) {
    throw new Error('Missing or invalid "timeline" field - must be an array');
  }

  // Validate timeline data points
  for (const point of data.timeline) {
    if (typeof point.date !== 'string') {
      throw new Error('Timeline data point missing "date" field');
    }
    if (typeof point.music_count !== 'number') {
      throw new Error('Timeline data point missing "music_count" field');
    }
    if (typeof point.video_count !== 'number') {
      throw new Error('Timeline data point missing "video_count" field');
    }
    if (typeof point.commit_count !== 'number') {
      throw new Error('Timeline data point missing "commit_count" field');
    }
  }

  // Check totals object
  if (!data.totals || typeof data.totals !== 'object') {
    throw new Error('Missing or invalid "totals" field - must be an object');
  }

  const totals = data.totals;
  if (typeof totals.total_music !== 'number') {
    throw new Error('Totals missing "total_music" field');
  }
  if (typeof totals.total_videos !== 'number') {
    throw new Error('Totals missing "total_videos" field');
  }
  if (typeof totals.total_commits !== 'number') {
    throw new Error('Totals missing "total_commits" field');
  }

  // Check correlations object
  if (!data.correlations || typeof data.correlations !== 'object') {
    throw new Error('Missing or invalid "correlations" field - must be an object');
  }

  const correlations = data.correlations;
  const patterns = ['music_only', 'video_only', 'both', 'neither'];
  
  for (const pattern of patterns) {
    if (!correlations[pattern] || typeof correlations[pattern] !== 'object') {
      throw new Error(`Correlations missing "${pattern}" pattern`);
    }
    if (typeof correlations[pattern].avg_commits !== 'number') {
      throw new Error(`Pattern "${pattern}" missing "avg_commits" field`);
    }
    if (typeof correlations[pattern].days !== 'number') {
      throw new Error(`Pattern "${pattern}" missing "days" field`);
    }
  }

  // Check insights object
  if (!data.insights || typeof data.insights !== 'object') {
    throw new Error('Missing or invalid "insights" field - must be an object');
  }

  const insights = data.insights;
  if (typeof insights.music_impact !== 'string') {
    throw new Error('Insights missing "music_impact" field');
  }
  if (typeof insights.video_impact !== 'string') {
    throw new Error('Insights missing "video_impact" field');
  }
  if (typeof insights.synergy_boost !== 'string') {
    throw new Error('Insights missing "synergy_boost" field');
  }
  if (typeof insights.best_pattern !== 'string') {
    throw new Error('Insights missing "best_pattern" field');
  }

  return true;
}

export async function loadCorrelations(): Promise<CorrelationData> {
  try {
    const response = await fetch('/correlations.json');
    
    if (!response.ok) {
      throw new Error(`Failed to fetch correlations.json: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Validate the data structure
    validateCorrelationData(data);
    
    return data as CorrelationData;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load correlation data: ${error.message}`);
    }
    throw new Error('Failed to load correlation data: Unknown error');
  }
}
