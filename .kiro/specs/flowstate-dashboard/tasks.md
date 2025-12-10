# Implementation Plan

## Project Setup and Configuration

- [x] 1. Initialize project structure and configuration files





  - Create directory structure: scripts/, data/, src/, public/
  - Create package.json with dependencies: vite, react, react-dom, typescript, recharts, tailwindcss, autoprefixer, postcss, lucide-react
  - Create requirements.txt with Python dependencies
  - Create vite.config.ts with standard Vite + React setup
  - Create tsconfig.json with strict mode enabled
  - Create tailwind.config.js with dark mode 'class' and content paths
  - Create postcss.config.js for Tailwind
  - Create index.html entry point
  - Create src/index.css with Tailwind directives
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

## Python Data Processing Scripts

- [x] 2. Implement parse_youtube.py script






  - Create scripts/parse_youtube.py file
  - Implement HTML parsing with BeautifulSoup to extract video entries
  - Implement categorization function with keyword matching (music, tutorial, entertainment, other)
  - Extract timestamp and derive date, hour, day_of_week fields
  - Create data/ directory if it doesn't exist
  - Output CSV to data/youtube_data.csv with correct columns
  - Add basic error handling with try-except around main logic
  - Add progress print statements
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Implement fetch_github.py script






  - Create scripts/fetch_github.py file
  - Implement GitHub API client with requests library
  - Fetch user repositories from /users/{username}/repos endpoint
  - Fetch commits from /repos/{username}/{repo}/commits endpoint (limit 100 per repo, 20 repos max)
  - Support GITHUB_TOKEN environment variable for authentication
  - Add 1-second delay between API requests
  - Extract repo, message, timestamp, date, hour, day_of_week from commits
  - Output CSV to data/github_data.csv
  - Handle HTTP errors (404, 403) gracefully and continue processing
  - Add progress print statements
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 4. Implement correlate_data.py script





  - Create scripts/correlate_data.py file
  - Load youtube_data.csv and github_data.csv with pandas
  - Merge datasets on date with outer join, fill missing values with 0
  - Calculate daily metrics: youtube_count, commit_count per date
  - Calculate music_correlation: group by category, compute avg_commits and sample_size
  - Calculate insights: best_hours (top 3 hours with most commits), top_category (max avg_commits), total_videos, total_commits
  - Format best_hours as time range string (e.g., "10 PM - 2 AM")
  - Create public/ directory if it doesn't exist
  - Output JSON to public/correlations.json with schema: {timeline, music_correlation, insights}
  - Add basic error handling and progress messages
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 3.10_

## React TypeScript Types and Utilities

- [x] 5. Implement TypeScript types and data loader





  - Create src/utils/types.ts with interfaces: TimelineDataPoint, CategoryData, Insights, CorrelationData
  - Create src/utils/dataLoader.ts with loadCorrelations() async function
  - Implement validateCorrelationData() type guard to check required fields
  - Add basic error handling in loadCorrelations() with try-catch
  - Throw descriptive errors for missing fields
  - _Requirements: 4.1, 4.4_

## React Dashboard Components

- [x] 6. Implement main Dashboard component





  - Create src/components/Dashboard.tsx
  - Add state: data (CorrelationData | null), loading (boolean), error (string | null)
  - Call loadCorrelations() on component mount
  - Render loading state: spinner with "Loading FlowState insights..." message
  - Render error state: error message with "Make sure you ran Python scripts" text
  - Render success state: header + InsightCards + ActivityTimeline + MusicCorrelation
  - Style header with "FlowState" title (gradient red-to-green), subtitle, and platform badges (YouTube red, GitHub green)
  - Use dark background (#0f172a), max-width 1400px, centered layout
  - _Requirements: 4.1, 4.2, 4.3, 4.5, 4.6, 4.7_

- [x] 7. Implement ActivityTimeline component





  - Create src/components/ActivityTimeline.tsx
  - Accept props: { data: TimelineDataPoint[] }
  - Filter data to last 3.5 months (105 days)
  - Implement Recharts LineChart with dual Y-axes
  - Configure left Y-axis (yAxisId="left") for youtube_count with RED line (#ef4444)
  - Configure right Y-axis (yAxisId="right") for commit_count with GREEN line (#10b981)
  - Add X-axis for dates
  - Add legend: "YouTube Videos" (red) + "GitHub Commits" (green)
  - Add horizontal grid lines (#334155)
  - Style tooltip with dark background and colored values
  - Make responsive with height 400px
  - Add chart title "Activity Timeline" with gradient text
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7_

- [x] 8. Implement MusicCorrelation component





  - Create src/components/MusicCorrelation.tsx
  - Accept props: { data: CategoryData[] }
  - Implement Recharts BarChart with categories on X-axis, avg_commits on Y-axis
  - Apply bar gradient from YouTube red (#ef4444) to GitHub green (#10b981)
  - Set opacity to 0.5 for bars where sample_size < 5
  - Find category with max avg_commits and display label above chart in green text
  - Style tooltip with dark background showing category, avg_commits, sample_size
  - Make responsive with height 350px
  - Add chart title "Music vs Coding Productivity"
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. Implement InsightCards component





  - Create src/components/InsightCards.tsx
  - Accept props: { insights: Insights }
  - Create 3 cards in grid layout (3 columns desktop, 1 column mobile)
  - Card 1: "Best Coding Hours" with Clock icon (green), display insights.best_hours, green border on hover
  - Card 2: "Top Category" with Music icon (red), display insights.top_category, red border on hover
  - Card 3: "Total Activity" with BarChart icon (gradient), display "{total_videos} videos • {total_commits} commits", gradient border on hover
  - Style each card: dark background (#1e293b), border (#334155), rounded corners, padding
  - Add hover effects: lift (scale-105), shadow with colored glow, smooth transitions
  - Use lucide-react for icons
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

## Application Entry Points

- [x] 10. Implement App and main entry points





  - Create src/App.tsx that renders Dashboard component
  - Wrap Dashboard in div with dark background, padding, and subtle gradient overlay
  - Create src/main.tsx with React 18 createRoot
  - Add 'dark' class to document.documentElement
  - Import './index.css'
  - Mount App component to root element
  - _Requirements: 4.6, 10.5_

## Documentation and Deployment

- [x] 11. Create README.md with setup and usage instructions





  - Add project title "FlowState" and tagline "YouTube × GitHub Productivity Insights"
  - List features: timeline visualization, music correlation, insights cards
  - Document tech stack: Python, React, Vite, Recharts, Tailwind, AWS S3
  - Add setup instructions: pip install, npm install
  - Add usage instructions: run parse_youtube.py, fetch_github.py, correlate_data.py, then npm run dev
  - Add deployment instructions: npm run build, aws s3 sync
  - Document color scheme: YouTube Red (#ef4444) + GitHub Green (#10b981)
  - Add note: "Built for Kiro Heroes Week 3: The Data Weaver"
  - _Requirements: 10.6_

- [x] 12. Final verification and manual testing





  - Run all Python scripts with real data and verify CSV outputs
  - Run npm run dev and verify dashboard loads correctly
  - Check that all charts render with correct colors (red for YouTube, green for GitHub)
  - Verify loading and error states work
  - Test responsive layout on mobile viewport
  - Verify insights make sense given the data
  - Run npm run build and verify dist/ output is ready for S3 deployment
  - _Requirements: All_
