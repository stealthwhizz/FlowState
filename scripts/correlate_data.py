"""
Correlate YouTube watch history with GitHub commit data for three-source analysis.

This script merges youtube_data.csv and github_data.csv to generate
insights about music, videos, and coding productivity patterns.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any


def load_and_merge_data() -> pd.DataFrame:
    """
    Load CSVs and merge on date with outer join.
    
    Returns:
        Merged DataFrame with both YouTube and GitHub data
    """
    print("Loading data files...")
    
    # Load YouTube data
    youtube_path = 'data/youtube_data.csv'
    if not os.path.exists(youtube_path):
        raise FileNotFoundError(f"YouTube data not found: {youtube_path}")
    youtube_df = pd.read_csv(youtube_path)
    print(f"  Loaded {len(youtube_df)} YouTube entries")
    
    # Load GitHub data
    github_path = 'data/github_data.csv'
    if not os.path.exists(github_path):
        raise FileNotFoundError(f"GitHub data not found: {github_path}")
    github_df = pd.read_csv(github_path)
    print(f"  Loaded {len(github_df)} GitHub entries")
    
    # Convert date columns to string and filter out invalid dates
    youtube_df['date'] = youtube_df['date'].astype(str)
    github_df['date'] = github_df['date'].astype(str)
    
    # Filter out rows with invalid dates (nan, empty, etc.)
    youtube_df = youtube_df[youtube_df['date'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
    github_df = github_df[github_df['date'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
    
    print(f"  After filtering: {len(youtube_df)} YouTube entries, {len(github_df)} GitHub entries")
    
    # Merge on date with outer join
    print("Merging datasets on date...")
    merged_df = pd.merge(
        youtube_df,
        github_df,
        on='date',
        how='outer',
        suffixes=('_youtube', '_github')
    )
    
    # Fill missing values with 0 for numeric columns
    merged_df = merged_df.fillna({
        'hour_youtube': 0,
        'hour_github': 0
    })
    
    print(f"  Merged dataset contains {len(merged_df)} date entries")
    
    return merged_df


def calculate_daily_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate music_count, video_count, commit_count per date for three-source analysis.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        List of timeline data points with three sources
    """
    print("Calculating daily metrics for three sources...")
    
    # Get all unique dates from both datasets
    all_dates = pd.concat([
        df[df['title'].notna()]['date'],
        df[df['repo'].notna()]['date']
    ]).unique()
    
    timeline = []
    
    for date in sorted(all_dates):
        # Count music videos for this date
        music_count = len(df[(df['date'] == date) & (df['category'] == 'music')])
        
        # Count non-music videos for this date
        video_count = len(df[(df['date'] == date) & (df['category'] == 'video')])
        
        # Count commits for this date
        commit_count = len(df[(df['date'] == date) & (df['repo'].notna())])
        
        timeline.append({
            'date': date,
            'music_count': music_count,
            'video_count': video_count,
            'commit_count': commit_count
        })
    
    print(f"  Calculated three-source metrics for {len(timeline)} dates")
    
    return timeline


def calculate_three_source_correlations(timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate correlations between music, videos, and commits for four patterns.
    
    Args:
        timeline: Daily metrics with music_count, video_count, commit_count
        
    Returns:
        Dictionary with correlation data and insights
    """
    print("Calculating three-source correlations...")
    
    if not timeline:
        print("  Warning: No timeline data found")
        return {}
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(timeline)
    
    # Calculate daily patterns
    df['has_music'] = df['music_count'] > 0
    df['has_videos'] = df['video_count'] > 0
    
    # Four patterns: music_only, video_only, both, neither
    music_only_days = df[(df['has_music']) & (~df['has_videos'])]
    video_only_days = df[(~df['has_music']) & (df['has_videos'])]
    both_days = df[(df['has_music']) & (df['has_videos'])]
    neither_days = df[(~df['has_music']) & (~df['has_videos'])]
    
    # Calculate average commits for each pattern
    correlations = {
        'music_only': {
            'avg_commits': round(music_only_days['commit_count'].mean() if len(music_only_days) > 0 else 0, 1),
            'days': len(music_only_days)
        },
        'video_only': {
            'avg_commits': round(video_only_days['commit_count'].mean() if len(video_only_days) > 0 else 0, 1),
            'days': len(video_only_days)
        },
        'both': {
            'avg_commits': round(both_days['commit_count'].mean() if len(both_days) > 0 else 0, 1),
            'days': len(both_days)
        },
        'neither': {
            'avg_commits': round(neither_days['commit_count'].mean() if len(neither_days) > 0 else 0, 1),
            'days': len(neither_days)
        }
    }
    
    # Calculate insights
    baseline = correlations['neither']['avg_commits']
    
    # Music impact: days with music vs days without music
    music_days = df[df['has_music']]
    no_music_days = df[~df['has_music']]
    
    music_avg = music_days['commit_count'].mean() if len(music_days) > 0 else 0
    no_music_avg = no_music_days['commit_count'].mean() if len(no_music_days) > 0 else 0
    music_impact = round(((music_avg - no_music_avg) / no_music_avg * 100) if no_music_avg > 0 else 0, 1)
    
    # Video impact: days with videos vs days without videos
    video_days = df[df['has_videos']]
    no_video_days = df[~df['has_videos']]
    
    video_avg = video_days['commit_count'].mean() if len(video_days) > 0 else 0
    no_video_avg = no_video_days['commit_count'].mean() if len(no_video_days) > 0 else 0
    video_impact = round(((video_avg - no_video_avg) / no_video_avg * 100) if no_video_avg > 0 else 0, 1)
    
    # Synergy boost: both vs baseline
    synergy_boost = round(((correlations['both']['avg_commits'] - baseline) / baseline * 100) if baseline > 0 else 0, 1)
    
    # Best pattern: highest average commits
    best_pattern_key = max(correlations.keys(), key=lambda k: correlations[k]['avg_commits'])
    best_pattern = best_pattern_key.replace('_', ' ').title()
    
    insights = {
        'music_impact': f"{music_impact:+.1f}%",
        'video_impact': f"{video_impact:+.1f}%", 
        'synergy_boost': f"{synergy_boost:+.1f}%",
        'best_pattern': best_pattern
    }
    
    print(f"  Music Impact: {insights['music_impact']}")
    print(f"  Video Impact: {insights['video_impact']}")
    print(f"  Synergy Boost: {insights['synergy_boost']}")
    print(f"  Best Pattern: {insights['best_pattern']}")
    
    return {
        'correlations': correlations,
        'insights': insights
    }


def calculate_totals(timeline: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate total counts for all three sources.
    
    Args:
        timeline: Daily metrics data
        
    Returns:
        Dictionary with total counts
    """
    print("Calculating totals...")
    
    if not timeline:
        return {'total_music': 0, 'total_videos': 0, 'total_commits': 0}
    
    df = pd.DataFrame(timeline)
    
    totals = {
        'total_music': int(df['music_count'].sum()),
        'total_videos': int(df['video_count'].sum()),
        'total_commits': int(df['commit_count'].sum())
    }
    
    print(f"  Total Music: {totals['total_music']}")
    print(f"  Total Videos: {totals['total_videos']}")
    print(f"  Total Commits: {totals['total_commits']}")
    
    return totals


def export_json(data: Dict[str, Any], output_path: str):
    """
    Write correlations.json with proper formatting.
    
    Args:
        data: Correlation data dictionary
        output_path: Path to output JSON file
    """
    print(f"Exporting JSON to: {output_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        print(f"  Creating directory: {output_dir}/")
        os.makedirs(output_dir)
    
    # Write JSON with pretty formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Successfully wrote {output_path}")


def main():
    """Main execution function."""
    try:
        print("=" * 60)
        print("Three-Source FlowState Analysis")
        print("Music × Videos × Commits")
        print("=" * 60)
        
        # Load and merge data
        merged_df = load_and_merge_data()
        
        # Calculate daily metrics for three sources
        timeline = calculate_daily_metrics(merged_df)
        
        # Calculate totals
        totals = calculate_totals(timeline)
        
        # Calculate three-source correlations and insights
        correlation_results = calculate_three_source_correlations(timeline)
        
        # Prepare output data with new three-source schema
        correlation_data = {
            'timeline': timeline,
            'totals': totals,
            'correlations': correlation_results.get('correlations', {}),
            'insights': correlation_results.get('insights', {})
        }
        
        # Export to JSON
        output_path = 'public/correlations.json'
        export_json(correlation_data, output_path)
        
        print("=" * 60)
        print("✓ Three-source analysis completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure you have run:")
        print("  1. python scripts/parse_youtube.py data/watch-history.html")
        print("  2. python scripts/fetch_github.py <username>")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
