# FlowState Dashboard - Design Document

## Overview

FlowState is an MVP productivity analytics system that combines YouTube watch history with GitHub commit data to reveal insights about coding patterns. The system architecture consists of two main components:

1. **Data Pipeline (Python)**: Three scripts that parse, fetch, and correlate data from YouTube and GitHub
2. **Visualization Dashboard (React)**: A web application that displays interactive charts and insights

The data flows unidirectionally: Python scripts generate a static JSON file that the React application consumes. This architecture enables simple deployment as a static site while maintaining separation between data processing and visualization.

**MVP Scope:** This is a working prototype focused on core functionality. No automated testing - validation happens through visual verification with real data. The goal is to get insights quickly, not production-grade code.

**Time Budget:**
- Python scripts: 4 hours
- React dashboard: 6 hours  
- Deployment: 2 hours
- **Total: 12 hours**

**What We're Cutting:**
- ❌ Property-based tests
- ❌ HourlyHeatmap component
- ❌ Tutorial lag calculation
- ❌ Flow trigger detection
- ❌ Comprehensive error handling
- ❌ Date gap filling

**What We're Keeping:**
- ✅ YouTube parsing with categorization
- ✅ GitHub commit fetching
- ✅ Basic correlation (music vs coding)
- ✅ 2-3 visualizations (timeline + bar chart + cards)
- ✅ Simple S3 deployment

## Architecture

### High-Level Architecture

```
┌─────────────────────┐
│  Google Takeout     │
│  (watch-history)    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐      ┌─────────────────────┐
│ parse_youtube.py    │─────>│  youtube_data.csv   │
└─────────────────────┘      └──────────┬──────────┘
                                        │
┌─────────────────────┐                │
│   GitHub API        │                │
└──────────┬──────────┘                │
           │                            │
           v                            v
┌─────────────────────┐      ┌─────────────────────┐
│ fetch_github.py     │─────>│  github_data.csv    │
└─────────────────────┘      └──────────┬──────────┘
                                        │
                                        v
                             ┌─────────────────────┐
                             │ correlate_data.py   │
                             └──────────┬──────────┘
                                        │
                                        v
                             ┌─────────────────────┐
                             │ correlations.json   │
                             └──────────┬──────────┘
                                        │
                                        v
                             ┌─────────────────────┐
                             │  React Dashboard    │
                             │  (Vite + TS)        │
                             └─────────────────────┘
```

### Technology Stack

**Frontend:**
- Vite 5.x (build tool)
- React 18 (UI framework)
- TypeScript 5 (type safety)
- Tailwind CSS (styling)
- Recharts 2.5+ (charting library)
- lucide-react (icons)

**Backend/Data Processing:**
- Python 3.10+
- beautifulsoup4 4.12.2 (HTML parsing)
- pandas 2.0.3 (data manipulation)
- requests 2.31.0 (HTTP client)
- lxml 4.9.3 (XML/HTML parser)

**Deployment:**
- AWS S3 (static hosting)
- CloudFront (optional CDN)

## Components and Interfaces

### Python Scripts

#### parse_youtube.py

**Purpose:** Parse Google Takeout watch history HTML and extract structured video data.

**Input:**
- File path to `watch-history.html` (Google Takeout export)

**Output:**
- CSV file at `data/youtube_data.csv`

**Key Functions:**
```python
def parse_watch_history(html_path: str) -> pd.DataFrame:
    """Parse YouTube watch history HTML and return DataFrame"""
    
def categorize_video(title: str) -> str:
    """Categorize video based on title keywords"""
    # Returns: "music" | "tutorial" | "entertainment" | "other"
    
def extract_datetime_fields(timestamp: str) -> dict:
    """Extract date, hour, day_of_week from timestamp"""
```

**Categorization Logic:**
- **music**: keywords like "music", "song", "beats", "lofi", "playlist", "mix", "audio"
- **tutorial**: keywords like "tutorial", "learn", "how to", "guide", "course", "programming", "coding"
- **entertainment**: keywords like "vlog", "gaming", "comedy", "stream", "podcast"
- **other**: default fallback

**Error Handling:**
- Wrap HTML parsing in try-except to handle malformed entries
- Log skipped entries but continue processing
- Validate timestamp format before parsing

#### fetch_github.py

**Purpose:** Fetch commit history from GitHub API for a specified user.

**Input:**
- Username (command-line argument or environment variable)
- Optional: GITHUB_TOKEN environment variable

**Output:**
- CSV file at `data/github_data.csv`

**Key Functions:**
```python
def fetch_user_repos(username: str, token: Optional[str]) -> List[dict]:
    """Fetch repository list for user"""
    
def fetch_repo_commits(username: str, repo: str, token: Optional[str], limit: int = 100) -> List[dict]:
    """Fetch commits for a specific repository"""
    
def extract_commit_data(commit: dict) -> dict:
    """Extract relevant fields from commit object"""
```

**API Endpoints:**
- `GET /users/{username}/repos` - List repositories
- `GET /repos/{username}/{repo}/commits` - List commits

**Rate Limiting:**
- 1-second delay between requests
- Respect GitHub API rate limits (60/hour unauthenticated, 5000/hour authenticated)
- Limit to 20 repositories maximum
- Limit to 100 commits per repository

**Error Handling:**
- Handle 404 (not found), 403 (forbidden), 401 (unauthorized)
- Handle network timeouts and connection errors
- Log errors but continue with remaining repositories

#### correlate_data.py

**Purpose:** Merge YouTube and GitHub data, calculate metrics, and generate insights.

**Input:**
- `data/youtube_data.csv`
- `data/github_data.csv`

**Output:**
- `public/correlations.json`

**Key Functions:**
```python
def load_and_merge_data() -> pd.DataFrame:
    """Load CSVs and merge on date with outer join"""
    
def calculate_daily_metrics(df: pd.DataFrame) -> List[dict]:
    """Calculate youtube_count, commit_count, activity_score per date"""
    
def calculate_music_correlation(df: pd.DataFrame) -> List[dict]:
    """Group by category and calculate avg commits"""
    
def generate_hourly_heatmap(df: pd.DataFrame) -> List[dict]:
    """Create heatmap data for day_of_week × hour"""
    
def calculate_insights(df: pd.DataFrame) -> dict:
    """Generate all insight metrics"""
    
def export_json(data: dict, output_path: str):
    """Write correlations.json with proper formatting"""
```

**Insight Calculations (MVP Simplified):**

1. **Best Hours:** Find top 3 hours with most commits, format as time range (e.g., "10 PM - 2 AM")
2. **Top Category:** Category with highest avg_commits (simple max, no sample size filter for MVP)
3. **Total Videos:** Count of all YouTube videos in dataset
4. **Total Commits:** Count of all GitHub commits in dataset

### React Components

#### Type Definitions (types.ts)

```typescript
export interface TimelineDataPoint {
  date: string;
  youtube_count: number;
  commit_count: number;
  activity_score: number;
}

export interface CategoryData {
  category: string;
  avg_commits: number;
  sample_size: number;
}

export interface Insights {
  best_hours: string;
  top_category: string;
  total_videos: number;
  total_commits: number;
}

export interface CorrelationData {
  timeline: TimelineDataPoint[];
  music_correlation: CategoryData[];
  insights: Insights;
}
```

#### Data Loader (dataLoader.ts)

```typescript
export async function loadCorrelations(): Promise<CorrelationData> {
  // Fetch /correlations.json
  // Validate structure
  // Return typed data
}

export function validateCorrelationData(data: any): data is CorrelationData {
  // Type guard checking all required fields
  // Return boolean
}
```

**Validation Rules:**
- Check presence of all top-level keys
- Validate array types for timeline, music_correlation, hourly_heatmap
- Validate object structure for insights and metadata
- Throw descriptive errors for missing/invalid fields

#### Dashboard.tsx

**Purpose:** Main container component that orchestrates data loading and rendering.

**State:**
```typescript
const [data, setData] = useState<CorrelationData | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Layout (MVP - 3 components):**
```
┌─────────────────────────────────────┐
│  Header: FlowState                  │
│  Subtitle: YouTube × GitHub...      │
├─────────────────────────────────────┤
│  InsightCards (3 cards)             │
├─────────────────────────────────────┤
│  ActivityTimeline                   │
├─────────────────────────────────────┤
│  MusicCorrelation                   │
└─────────────────────────────────────┘
```

**Styling:**
- Background: #0f172a (slate-950)
- Spacing: 6-8 units between sections
- Max width: 1400px, centered
- Padding: responsive (4 on mobile, 8 on desktop)

#### ActivityTimeline.tsx

**Purpose:** Display dual-axis line chart showing YouTube and GitHub activity over time.

**Props:**
```typescript
interface ActivityTimelineProps {
  data: TimelineDataPoint[];
}
```

**Chart Configuration:**
- Chart type: LineChart (Recharts)
- Dimensions: Responsive, min height 400px
- X-axis: date (last 3.5 months only)
- Left Y-axis: youtube_count (blue #3b82f6)
- Right Y-axis: commit_count (green #10b981)
- Grid: Horizontal lines, stroke #334155
- Tooltip: Custom dark theme

**Data Processing:**
- Filter to last 3.5 months (105 days)
- Fill date gaps with zero values
- Sort by date ascending

#### MusicCorrelation.tsx

**Purpose:** Display bar chart showing average commits per video category.

**Props:**
```typescript
interface MusicCorrelationProps {
  data: CategoryData[];
}
```

**Chart Configuration:**
- Chart type: BarChart (Recharts)
- Dimensions: Responsive, height 350px
- X-axis: category
- Y-axis: avg_commits
- Bar fill: Gradient from #8b5cf6 to #6366f1
- Opacity: 0.5 if sample_size < 5, else 1.0
- Tooltip: Shows category, avg_commits, sample_size

**Best Category Label:**
- Find max avg_commits
- Display above chart: "Best for coding: {category}"
- Style: text-lg, purple color

#### InsightCards.tsx

**Purpose:** Display four key insights as styled cards.

**Props:**
```typescript
interface InsightCardsProps {
  insights: Insights;
}
```

**Card Configuration (MVP - 3 cards):**

| Card | Icon | Insight Key | Description |
|------|------|-------------|-------------|
| Best Coding Hours | Clock | best_hours | Top productive time periods |
| Top Category | Music | top_category | Best video category for coding |
| Total Stats | BarChart | total_videos, total_commits | Overall activity metrics |

**Card Styling:**
- Background: #1e293b
- Border: 1px solid #334155
- Border radius: 0.5rem
- Padding: 1.5rem
- Hover: shadow-lg, transform scale 1.02
- Transition: all 200ms

**Grid Layout:**
- Desktop: 3 columns (for 3 cards)
- Mobile: 1 column
- Gap: 1.5rem

## Data Models

### CSV Schemas

**youtube_data.csv:**
```
title,url,timestamp,date,hour,day_of_week,category
"Video Title","https://youtube.com/watch?v=...","2025-12-09T14:30:00Z","2025-12-09",14,"Tuesday","tutorial"
```

**github_data.csv:**
```
repo,message,timestamp,date,hour,day_of_week
"username/repo-name","Commit message","2025-12-09T15:45:00Z","2025-12-09",15,"Tuesday"
```

### JSON Schema (correlations.json) - MVP Simplified

```json
{
  "timeline": [
    {
      "date": "2025-12-09",
      "youtube_count": 12,
      "commit_count": 5
    }
  ],
  "music_correlation": [
    {
      "category": "music",
      "avg_commits": 6.5,
      "sample_size": 45
    }
  ],
  "insights": {
    "best_hours": "10 PM - 2 AM",
    "top_category": "music",
    "total_videos": 1778,
    "total_commits": 206
  }
}
```

**Note:** Removed hourly_heatmap, tutorial_lag, flow_triggers, and activity_score for MVP simplicity.


## Correctness Properties

**MVP Note:** For this MVP, we are NOT implementing automated property-based tests. The properties below serve as design guidelines and will be validated through manual testing with real data.

### Core Functional Properties (Manual Validation)

**Property 1: Video categorization consistency**
*For any* video title string, the categorization function should return exactly one of the four valid categories: "music", "tutorial", "entertainment", or "other"
**Validates: Requirements 1.2**
**Manual Test:** Run script on real YouTube data, spot-check categorizations

**Property 2: CSV output schema compliance**
*For any* successful parse operation, the output CSV file should contain exactly the specified columns in the correct order
**Validates: Requirements 1.5**
**Manual Test:** Open generated CSV, verify column headers

**Property 3: Date merge completeness**
*For any* two datasets with overlapping and non-overlapping dates, an outer join should include all dates from both datasets
**Validates: Requirements 3.2**
**Manual Test:** Check that timeline includes dates with only YouTube or only GitHub activity

**Property 4: Category aggregation correctness**
*For any* distribution of videos across categories, grouping by category and calculating average commits should produce reasonable averages
**Validates: Requirements 3.4**
**Manual Test:** Verify bar chart values make sense given the data

**Property 5: Top category identification**
*For any* set of categories with average commit values, the top_category insight should identify the category with highest average commits
**Validates: Requirements 3.7**
**Manual Test:** Compare insight card to bar chart, verify they match

## Error Handling (MVP - Basic Only)

### Python Scripts

**Basic error handling:**
- Wrap main logic in try-except, print error and exit
- Check if input files exist before processing
- Create output directories if they don't exist
- Print progress messages so user knows what's happening

**No fancy error recovery** - if something breaks, let it fail loudly so it's obvious.

### React Application

**Basic error handling:**
- Try-catch around fetch, show error message if it fails
- Check if JSON has required fields, show error if missing
- Loading spinner while fetching
- Basic error message: "Failed to load data. Make sure you ran the Python scripts."

**No error boundaries or complex validation** - keep it simple.

## Testing Strategy (MVP)

**NO AUTOMATED TESTING** - This is an MVP focused on speed to insights.

### Manual Validation Approach

**Python Scripts:**
1. Run each script with your real data
2. Inspect CSV outputs in Excel/text editor
3. Verify categorizations make sense
4. Check for obvious errors or crashes

**React Dashboard:**
1. Run `npm run dev` and open in browser
2. Verify all charts render
3. Check that numbers make sense
4. Test on mobile viewport
5. Verify loading/error states by temporarily breaking JSON

**End-to-End Validation:**
1. Run complete pipeline: parse → fetch → correlate → build → view
2. Spot-check a few data points manually
3. Verify insights are interesting and actionable
4. If something looks wrong, add console.log and debug

**Quality Bar:** "Good enough to get insights from real data" - not production-grade.

## Deployment Strategy

### Build Process

1. **Data Generation:**
   ```bash
   python scripts/parse_youtube.py data/watch-history.html
   python scripts/fetch_github.py <username>
   python scripts/correlate_data.py
   ```

2. **Frontend Build:**
   ```bash
   npm run build
   # Outputs to dist/ directory
   ```

3. **Verification:**
   - Verify correlations.json exists in dist/
   - Check file sizes are reasonable
   - Validate JSON structure

### AWS S3 Deployment

**S3 Bucket Configuration:**
- Enable static website hosting
- Set index document: index.html
- Set error document: index.html (for SPA routing)
- Configure CORS if needed

**Upload Process:**
```bash
aws s3 sync dist/ s3://flowstate-dashboard/ --delete
aws s3 cp dist/correlations.json s3://flowstate-dashboard/correlations.json
```

**CloudFront (Optional):**
- Create distribution pointing to S3 bucket
- Enable HTTPS with ACM certificate
- Set default root object: index.html
- Configure error pages for SPA

**Security:**
- Block public access to S3 bucket
- Use CloudFront with Origin Access Identity
- Enable S3 bucket encryption
- Set appropriate cache headers

### Environment Variables

**Python Scripts:**
- `GITHUB_TOKEN`: GitHub personal access token (optional)
- `GITHUB_USERNAME`: Default username for fetching commits

**Build Process:**
- No environment variables needed for React build
- All data is static JSON

### Monitoring

- CloudWatch metrics for S3 requests
- CloudFront access logs
- Monitor data freshness (last update timestamp)
- Set up alerts for failed builds

## Performance Considerations (MVP)

**Python Scripts:**
- Limit to 20 repos, 100 commits each (reasonable for personal use)
- 1-second delay between API requests (avoid rate limits)

**React Application:**
- Default Vite + React performance is fine for MVP
- No optimization needed unless bundle is > 1MB

**If it's slow, we'll optimize later.** MVP priority is working code, not fast code.

## Out of Scope for MVP

**Not implementing:**
- Accessibility features (ARIA, screen readers, keyboard nav)
- Responsive optimization beyond basic Tailwind breakpoints
- Advanced error recovery
- Data export features
- Authentication
- Real-time updates
- Custom date ranges
- Filtering

**If this MVP proves useful, we can add these later.**
