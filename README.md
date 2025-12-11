# FlowState

**YouTube × GitHub Productivity Insights**

FlowState is a productivity analytics dashboard that correlates your YouTube watch history with GitHub commit patterns to discover insights about your coding productivity. Visualize how your content consumption aligns with your development activity and optimize your workflow for peak performance.

## 🚀 Live Demo

- **AWS S3**: [http://flowstate-stealthwhizz.s3-website.ap-south-1.amazonaws.com](http://flowstate-stealthwhizz.s3-website.ap-south-1.amazonaws.com)
- **GitHub Pages**: [https://stealthwhizz.github.io/FlowState/](https://stealthwhizz.github.io/FlowState/)

## 📸 Screenshots

### Main Dashboard
![FlowState Dashboard](Images/main.png)

### Productivity Insights
![FlowState Analytics](Images/flowstate.png)

### Correlation Analysis
![FlowState Correlation](Images/flowstate2.png)

### Architecture Overview
![System Architecture](Images/arch.png)

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
