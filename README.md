# FlowState
![FlowState ](Images/cover.png)

**YouTube × GitHub Productivity Insights**

FlowState is a productivity analytics dashboard that correlates your YouTube watch history with GitHub commit patterns to discover insights about your coding productivity. Visualize how your content consumption aligns with your development activity and optimize your workflow for peak performance.

## 🚀 Live Demo

- **AWS S3**: [http://flowstate-stealthwhizz.s3-website.ap-south-1.amazonaws.com](http://flowstate-stealthwhizz.s3-website.ap-south-1.amazonaws.com)
- **GitHub Pages**: [https://stealthwhizz.github.io/FlowState/](https://stealthwhizz.github.io/FlowState/)

## 📸 Screenshots

### Main Dashboard
![FlowState Dashboard](Images/main.png)

### Correlation Analysis
![FlowState Correlation](Images/flowstate2.png)

### Architecture Overview
![System Architecture](Images/arch.png)

### Tech Stack
![Tech Stack](Images/techstack.png)

## 🎥 Demo Video

Watch Kiro working on making the MCP server: https://youtu.be/sqK0hvhUxl4

## Features

- **Timeline Visualization**: Interactive dual-axis chart showing YouTube videos watched and GitHub commits over time
- **Music Correlation**: Bar chart analysis revealing which video categories boost your coding productivity
- **Insights Cards**: Key metrics including best coding hours, top productivity category, and total activity stats

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Recharts, Tailwind CSS
- **Data Processing**: Python 3.10+, BeautifulSoup4, Pandas, Requests
- **Deployment**: AWS S3 Static Hosting
- **Styling**: Dark theme with YouTube Red (#ef4444) + GitHub Green (#10b981) color scheme

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flowstate-dashboard
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

## Usage Instructions

### Step 1: Prepare Your Data

1. **Export YouTube Watch History**
   - Go to [Google Takeout](https://takeout.google.com)
   - Select "YouTube and YouTube Music" → "history" → "watch-history.html"
   - Download and place the file in the `data/` directory

2. **Set up GitHub Access (Optional)**
   ```bash
   export GITHUB_TOKEN=your_personal_access_token
   ```

### Step 2: Run Data Processing Scripts

Execute the Python scripts in order:

```bash
# Parse YouTube watch history
python scripts/parse_youtube.py data/watch-history.html

# Fetch GitHub commit data
python scripts/fetch_github.py <your-github-username>

# Generate correlation data
python scripts/correlate_data.py
```

### Step 3: Launch Dashboard

```bash
# Start development server
npm run dev
```

Open your browser to `http://localhost:5173` to view your FlowState dashboard.

## 🤖 MCP Server

FlowState includes a Model Context Protocol (MCP) server that exposes productivity insights through standardized tools. Use these tools with your MCP client to programmatically query and analyze your productivity data.

### Prerequisites

- Python 3.10 or higher
- MCP client compatible with STDIO transport

### Installation

Install the MCP server dependencies:

```bash
pip install 'mcp[cli]>=0.9.0'
```

### Running the MCP Server

Start the server with:

```bash
python scripts/mcp_server.py
```

You should see output like:

```
✓ Correlation data loaded successfully
  - Timeline entries: 45
  - Total commits: 127
  - Total music sessions: 89
  - Total videos: 34
  - Best pattern: both

Server initialized successfully
Available tools:
  - get_best_hours: Analyze optimal coding hours based on historical patterns
  - get_flow_state_pattern: Identify optimal music/video pattern for maximum productivity
  - analyze_productivity: Analyze productivity metrics for a specific date (YYYY-MM-DD)
  - get_music_impact: Analyze the impact of background music on coding productivity
  - predict_commits: Predict commit count based on planned music hours and video minutes
Available resources:
  - flowstate://dashboard: Access to FlowState dashboard (S3 or localhost fallback)
```

### Available Tools

#### 1. `get_best_hours` - Analyze Optimal Coding Hours

Analyzes your historical data to identify the best hours for coding based on day-of-week patterns.

**No parameters required**

**Response:**
```json
{
  "best_hours": [
    {
      "hour": 20,
      "avg_commits": 4.0,
      "day_pattern": "weekday"
    }
  ],
  "recommendation": "Peak productivity on weekday evenings (8-10 PM). Average 10.0 commits on productive weekdays.",
  "data_note": "Insights derived from day-of-week patterns..."
}
```

#### 2. `get_flow_state_pattern` - Identify Optimal Productivity Pattern

Analyzes correlations between music/video consumption and commits to find your optimal flow state pattern.

**No parameters required**

**Response:**
```json
{
  "pattern": "both",
  "avg_commits": 8.5,
  "boost_percentage": "+42.5%",
  "recommendation": "Use both music and videos for optimal productivity. The synergy between audio and visual content creates the best flow state.",
  "baseline_avg": 5.97,
  "days_analyzed": 15,
  "total_patterns": 4
}
```

#### 3. `analyze_productivity` - Analyze Specific Date

Analyzes your productivity metrics for a specific date (YYYY-MM-DD format).

**Parameters:**
- `date` (string, required): Date in YYYY-MM-DD format (e.g., "2024-01-15")

**Response:**
```json
{
  "date": "2024-01-15",
  "music_count": 3,
  "video_count": 2,
  "commit_count": 8,
  "productivity_score": 4.6,
  "productivity_level": "Moderate",
  "calculation_note": "Score = (commits×3 + music×1 + videos×1) ÷ 5"
}
```

**Error Response:**
```json
{
  "error": "Invalid date format. Use YYYY-MM-DD",
  "error_code": "INVALID_DATE_FORMAT",
  "suggestion": "Provided: 'invalid-date', Expected format: 'YYYY-MM-DD', Example: '2024-01-15'"
}
```

#### 4. `get_music_impact` - Analyze Music's Impact on Productivity

Compares your commit patterns on days with and without background music.

**No parameters required**

**Response:**
```json
{
  "music_boost_percentage": "+35.2%",
  "days_with_music": 12,
  "days_without_music": 8,
  "avg_commits_with_music": 8.42,
  "avg_commits_without_music": 6.23,
  "recommendation": "Music significantly boosts productivity! Consider listening to music while coding for optimal performance.",
  "analysis_context": {
    "total_days_analyzed": 20,
    "music_usage_percentage": "60.0%",
    "confidence": "high"
  }
}
```

#### 5. `predict_commits` - Predict Commit Count

Predicts your likely commit count based on planned music hours and video minutes.

**Parameters:**
- `music_hours` (float, required): Number of hours of music (must be non-negative)
- `video_minutes` (float, required): Number of minutes of videos (must be non-negative)

**Example:**
```bash
predict_commits 2.5 45
```

**Response:**
```json
{
  "predicted_commits": 9.2,
  "confidence_level": "high",
  "factors_considered": [
    "historical_music_impact",
    "video_consumption_patterns",
    "base_productivity",
    "correlation_analysis",
    "sufficient_historical_data"
  ],
  "prediction_context": {
    "music_coefficient": 2.456,
    "video_coefficient": 0.142,
    "historical_data_points": 45,
    "avg_historical_music": 1.8,
    "avg_historical_videos": 38.5
  },
  "input_validation": {
    "music_hours": 2.5,
    "video_minutes": 45,
    "parameters_valid": true
  }
}
```

### Resources

#### `flowstate://dashboard`

Access to your FlowState dashboard. Returns the S3 URL if `FLOWSTATE_DASHBOARD_URL` is configured, otherwise returns localhost fallback.

**Response:**
```json
{
  "url": "http://localhost:5173",
  "metadata": {
    "description": "FlowState Dashboard - Interactive visualization of productivity insights...",
    "content_type": "text/html",
    "last_modified": "2024-01-15T10:30:00.000Z",
    "deployment_type": "development",
    "resource_type": "dashboard",
    "version": "1.0.0"
  }
}
```

### MCP Client Configuration

To integrate the FlowState MCP server with your MCP client, add this configuration:

**Claude (claude_desktop_config.json):**
```json
{
  "mcpServers": {
    "flowstate": {
      "command": "python",
      "args": ["/path/to/FlowState/scripts/mcp_server.py"],
      "env": {
        "FLOWSTATE_DASHBOARD_URL": "https://your-s3-bucket.s3-website-region.amazonaws.com"
      }
    }
  }
}
```

### Environment Variables

- `FLOWSTATE_DASHBOARD_URL` (optional): S3 URL for your deployed FlowState dashboard. If not set, defaults to `http://localhost:5173`

### Error Handling

All tools provide consistent error responses with helpful suggestions:

```json
{
  "error": "Insufficient data for meaningful analysis",
  "error_code": "INSUFFICIENT_DATA",
  "suggestion": "Collect more data by running the FlowState pipeline over several days (current: 2 days, need: 5+)"
}
```

### Troubleshooting

**"Correlation data not found"**
- Ensure you've run the data processing pipeline: `python scripts/correlate_data.py`
- Verify `public/correlations.json` exists and contains valid data

**"Insufficient data for meaningful analysis"**
- The analysis requires a minimum amount of historical data
- Run the FlowState pipeline over several more days to collect more data

**"Invalid date format"**
- Use the format YYYY-MM-DD (e.g., 2024-01-15)
- Ensure the date exists in your timeline data

## Deployment Instructions

### Build for Production

```bash
# Create production build
npm run build
```

### Deploy to AWS S3

1. **Configure AWS CLI** (if not already done)
   ```bash
   aws configure
   ```

2. **Create S3 bucket and enable static hosting**
   ```bash
   aws s3 mb s3://your-flowstate-bucket
   aws s3 website s3://your-flowstate-bucket --index-document index.html
   ```

3. **Deploy to S3**
   ```bash
   aws s3 sync dist/ s3://your-flowstate-bucket/ --delete
   ```

4. **Access your dashboard**
   - Visit: `http://your-flowstate-bucket.s3-website-region.amazonaws.com`

## Color Scheme

FlowState uses a carefully designed color palette that reflects the data sources:

- **YouTube Red**: `#ef4444` - Used for YouTube-related data and metrics
- **GitHub Green**: `#10b981` - Used for GitHub-related data and metrics
- **Dark Theme**: Slate backgrounds (`#0f172a`, `#1e293b`) for optimal viewing

## Project Structure

```
flowstate-dashboard/
├── scripts/           # Python data processing scripts
│   ├── parse_youtube.py
│   ├── fetch_github.py
│   └── correlate_data.py
├── data/             # Generated CSV files
├── public/           # Static assets and generated JSON
├── src/              # React TypeScript source code
│   ├── components/   # Dashboard components
│   └── utils/        # Type definitions and data loading
└── dist/             # Production build output
```

## Troubleshooting

**Dashboard shows "Loading..." indefinitely**
- Ensure you've run all three Python scripts successfully
- Check that `public/correlations.json` exists and is valid JSON

**GitHub script fails with 403 errors**
- Set up a GitHub personal access token with repo permissions
- Export it as `GITHUB_TOKEN` environment variable

**Charts appear empty**
- Verify your data files contain entries in the expected date range
- Check browser console for JavaScript errors

---
