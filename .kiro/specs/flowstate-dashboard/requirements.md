# Requirements Document

## Introduction

FlowState is a productivity analytics dashboard that analyzes three distinct data sources to discover the science of coding flow: YouTube Music (background music while coding), YouTube Videos (tutorials, entertainment, learning content), and GitHub Commits (coding productivity). The system consists of Python data processing scripts that parse YouTube watch history into music vs video categories, fetch GitHub commits, and generate three-source correlation data, paired with a React TypeScript web application that visualizes these insights through interactive charts and metrics.

## Glossary

- **FlowState Dashboard**: The React TypeScript web application that displays three-source productivity insights
- **YouTube Music**: Videos where the primary purpose is listening to music while coding (background audio)
- **YouTube Videos**: All non-music content including tutorials, vlogs, entertainment, tech talks, and learning content
- **GitHub Commit Data**: Commit records fetched from GitHub API for a specified user
- **Three-Source Correlation**: Analysis combining music sessions, video consumption, and coding productivity
- **Music Impact**: Percentage boost in commits when listening to background music
- **Video Impact**: Percentage boost in commits after watching educational/entertainment videos
- **Synergy Boost**: Percentage boost in commits when combining both music and videos
- **Flow State Pattern**: The optimal combination of music and videos that maximizes coding productivity
- **Correlation Grid**: 2×2 matrix showing average commits for different consumption patterns
- **Python Scripts**: Data processing scripts (parse_youtube.py, fetch_github.py, correlate_data.py)
- **Data Pipeline**: The complete flow from raw data sources to three-source visualization-ready JSON

## Requirements

### Requirement 1

**User Story:** As a developer, I want to parse my YouTube watch history into music and video categories, so that I can analyze the distinct impact of background music versus active video consumption on my coding productivity.

#### Acceptance Criteria

1. WHEN the parse_youtube.py script receives a watch-history.html file, THE Python Scripts SHALL extract title, url, and timestamp for each video entry
2. WHEN categorizing videos, THE Python Scripts SHALL classify each video as either "music" or "video" based on title keywords
3. WHEN identifying music videos, THE Python Scripts SHALL match keywords including: music, song, beats, lofi, lo-fi, synthwave, playlist, mix, audio, official music video, lyrics, soundtrack, OST, jazz, classical, hip hop, edm, acoustic, ambient, chill, study music, background music, instrumental, piano, guitar, relaxing, meditation, focus music, 1 hour, 8 hour
4. WHEN identifying video content, THE Python Scripts SHALL classify all non-music content as "video" including tutorials, how-to, gaming, vlogs, tech talks, reviews, streams
5. WHEN processing timestamps, THE Python Scripts SHALL derive date, hour, and day_of_week fields from each timestamp
6. WHEN encountering malformed HTML, THE Python Scripts SHALL handle errors gracefully using try-except blocks and continue processing
7. WHEN parsing completes, THE Python Scripts SHALL output a CSV file at data/youtube_data.csv with columns: title, url, timestamp, date, hour, day_of_week, category

### Requirement 2

**User Story:** As a developer, I want to fetch my GitHub commit history via API, so that I can analyze my coding activity patterns.

#### Acceptance Criteria

1. WHEN the fetch_github.py script runs with a username, THE Python Scripts SHALL fetch repository lists from the GitHub API endpoint /users/{user}/repos
2. WHEN fetching commits, THE Python Scripts SHALL retrieve up to 100 commits per repository for a maximum of 20 repositories
3. WHEN a GITHUB_TOKEN environment variable exists, THE Python Scripts SHALL use it for authenticated API requests
4. WHEN making API requests, THE Python Scripts SHALL add a 1-second delay between requests to respect rate limiting
5. WHEN extracting commit data, THE Python Scripts SHALL derive repo, message, timestamp, date, hour, and day_of_week fields
6. WHEN encountering HTTP errors (404, 403) or network failures, THE Python Scripts SHALL handle them gracefully and continue processing
7. WHEN fetching completes, THE Python Scripts SHALL output a CSV file at data/github_data.csv

### Requirement 3

**User Story:** As a developer, I want to correlate my three data sources (YouTube Music, YouTube Videos, GitHub Commits), so that I can discover the science of my coding flow state.

#### Acceptance Criteria

1. WHEN the correlate_data.py script runs, THE Python Scripts SHALL load both youtube_data.csv and github_data.csv using pandas
2. WHEN merging datasets, THE Python Scripts SHALL perform an outer join on date and fill missing values with zero
3. WHEN calculating daily metrics, THE Python Scripts SHALL compute music_count, video_count, and commit_count for each date
4. WHEN analyzing three-source correlations, THE Python Scripts SHALL calculate average commits for four patterns: music_only, video_only, both, and neither
5. WHEN calculating music impact, THE Python Scripts SHALL compute percentage boost comparing days with music > 0 versus days with music = 0
6. WHEN calculating video impact, THE Python Scripts SHALL compute percentage boost comparing days with videos > 0 versus days with videos = 0
7. WHEN calculating synergy boost, THE Python Scripts SHALL compute percentage boost comparing days with both music > 0 AND videos > 0 versus baseline (neither)
8. WHEN identifying best pattern, THE Python Scripts SHALL determine the optimal combination of music and video consumption that maximizes commits
9. WHEN generating timeline data, THE Python Scripts SHALL include music_count, video_count, and commit_count for each date
10. WHEN correlation completes, THE Python Scripts SHALL output public/correlations.json with timeline, totals, correlations, and insights sections matching the three-source schema

### Requirement 4

**User Story:** As a user, I want to view a three-source dashboard that loads my correlation data, so that I can understand the science of my coding flow.

#### Acceptance Criteria

1. WHEN the FlowState Dashboard loads, THE FlowState Dashboard SHALL fetch correlations.json from the public directory
2. WHEN data is loading, THE FlowState Dashboard SHALL display a spinner with the message "Loading FlowState insights..."
3. WHEN data loading fails, THE FlowState Dashboard SHALL display an error message with troubleshooting text
4. WHEN data validation fails, THE FlowState Dashboard SHALL throw descriptive errors indicating which required fields are missing
5. WHEN data loads successfully, THE FlowState Dashboard SHALL render all five visualization components in order: header, insight cards, correlation grid, activity timeline
6. WHEN displaying the dashboard, THE FlowState Dashboard SHALL use a dark background color (#0f172a) with proper spacing between components
7. WHEN displaying the header, THE FlowState Dashboard SHALL show "FlowState" as the title and "The Science of Your Coding Flow" as the subtitle
8. WHEN displaying source badges, THE FlowState Dashboard SHALL show three badges: "🎵 Music" (orange #f97316), "📺 Videos" (red #ef4444), "💻 Commits" (green #10b981)

### Requirement 5

**User Story:** As a user, I want to see a timeline of my three data sources, so that I can visualize how music, videos, and coding patterns align over time.

#### Acceptance Criteria

1. WHEN rendering the activity timeline, THE FlowState Dashboard SHALL display a triple line chart with dual Y-axes
2. WHEN plotting music data, THE FlowState Dashboard SHALL use the left Y-axis with an orange line (#f97316) for music_count labeled "Music Sessions"
3. WHEN plotting video data, THE FlowState Dashboard SHALL use the left Y-axis with a red line (#ef4444) for video_count labeled "Videos Watched"
4. WHEN plotting GitHub data, THE FlowState Dashboard SHALL use the right Y-axis with a green line (#10b981) for commit_count labeled "GitHub Commits"
5. WHEN displaying the X-axis, THE FlowState Dashboard SHALL show dates for the last 3.5 months only
6. WHEN date gaps exist in the data range, THE FlowState Dashboard SHALL insert zero values to fill the gaps
7. WHEN hovering over data points, THE FlowState Dashboard SHALL display a tooltip showing music_count, video_count, and commit_count values
8. WHEN rendering the chart, THE FlowState Dashboard SHALL include horizontal grid lines, legend with colored dots, and use dark mode styling

### Requirement 6

**User Story:** As a user, I want to see a correlation grid showing how different consumption patterns affect my coding productivity, so that I can optimize my flow state.

#### Acceptance Criteria

1. WHEN rendering the correlation grid, THE FlowState Dashboard SHALL display a 2×2 matrix with four cells: Music Only, Videos Only, Neither, and Both
2. WHEN displaying Music Only cell, THE FlowState Dashboard SHALL show average commits with orange styling (#f97316) and percentage boost versus baseline
3. WHEN displaying Videos Only cell, THE FlowState Dashboard SHALL show average commits with red styling (#ef4444) and percentage boost versus baseline
4. WHEN displaying Neither cell, THE FlowState Dashboard SHALL show average commits as the baseline with neutral styling
5. WHEN displaying Both cell, THE FlowState Dashboard SHALL show average commits with gradient border (orange→red→green) and highlight as the optimal pattern
6. WHEN hovering over cells, THE FlowState Dashboard SHALL display enhanced styling with scale transform and detailed tooltip
7. WHEN rendering the grid, THE FlowState Dashboard SHALL use CSS Grid layout with proper spacing and dark mode styling

### Requirement 7

**User Story:** As a user, I want to see key productivity insights as cards, so that I can quickly understand my three-source coding patterns.

#### Acceptance Criteria

1. WHEN rendering insight cards, THE FlowState Dashboard SHALL display a 2×2 grid layout that collapses to 1 column on mobile
2. WHEN displaying the four cards, THE FlowState Dashboard SHALL show Music Impact, Video Impact, Synergy Boost, and Best Pattern
3. WHEN displaying Music Impact card, THE FlowState Dashboard SHALL use headphones icon (orange) and show percentage boost from background music
4. WHEN displaying Video Impact card, THE FlowState Dashboard SHALL use YouTube icon (red) and show percentage boost from learning videos
5. WHEN displaying Synergy Boost card, THE FlowState Dashboard SHALL use zap icon (gradient orange→red→green) and show percentage boost from combining both sources
6. WHEN displaying Best Pattern card, THE FlowState Dashboard SHALL use target icon (green) and show the optimal flow state pattern
7. WHEN rendering each card, THE FlowState Dashboard SHALL use dark background (#1e293b), border (#334155), rounded corners, and padding
8. WHEN hovering over cards, THE FlowState Dashboard SHALL display lift effect and colored glow matching the card's theme

### Requirement 8

**User Story:** As a user, I want the dashboard layout to clearly present the three-source analysis, so that I can understand the complete flow state story.

#### Acceptance Criteria

1. WHEN rendering the dashboard layout, THE FlowState Dashboard SHALL display components in this order: header with badges, insight cards, correlation grid, activity timeline
2. WHEN displaying the complete story, THE FlowState Dashboard SHALL convey that "Music provides focus, Videos provide knowledge, Together they create Flow State for maximum commits"
3. WHEN using the color palette, THE FlowState Dashboard SHALL consistently use orange (#f97316, #fb923c) for music, red (#ef4444, #f87171) for videos, and green (#10b981, #34d399) for commits
4. WHEN styling typography, THE FlowState Dashboard SHALL use gradient orange→red→green for the title, large bold text for card values, and green highlighting for positive percentages
5. WHEN implementing interactions, THE FlowState Dashboard SHALL provide hover effects on cards (lift + colored glow), chart lines (highlight + tooltip), and grid cells (scale + detail tooltip)

### Requirement 9

**User Story:** As a developer, I want the three-source dashboard to be responsive and mobile-friendly, so that I can view flow state insights on any device.

#### Acceptance Criteria

1. WHEN the FlowState Dashboard renders on mobile devices, THE FlowState Dashboard SHALL adapt the 2×2 grids to single-column layouts where appropriate
2. WHEN the triple-line chart renders on different screen sizes, THE FlowState Dashboard SHALL maintain readability and proper scaling for all three data sources
3. WHEN the correlation grid renders on mobile, THE FlowState Dashboard SHALL stack the 2×2 matrix vertically while preserving the visual hierarchy
4. WHEN the viewport width changes, THE FlowState Dashboard SHALL respond with appropriate breakpoints using Tailwind CSS

### Requirement 10

**User Story:** As a developer, I want the three-source application built with modern tooling and best practices, so that it is maintainable and production-ready.

#### Acceptance Criteria

1. WHEN TypeScript code is compiled, THE FlowState Dashboard SHALL use strict mode enabled with proper typing for three-source data structures
2. WHEN building the application, THE FlowState Dashboard SHALL use Vite as the build tool with React 18
3. WHEN styling components, THE FlowState Dashboard SHALL use Tailwind CSS with dark mode class strategy and the three-source color palette
4. WHEN rendering charts, THE FlowState Dashboard SHALL use Recharts version 2.5 or higher for the triple-line timeline visualization
5. WHEN the application initializes, THE FlowState Dashboard SHALL add the 'dark' class to document.documentElement
6. WHEN errors occur, THE FlowState Dashboard SHALL handle them gracefully using try-catch blocks with descriptive error messages
7. WHEN processing three-source data, THE FlowState Dashboard SHALL validate the presence of music_count, video_count, and commit_count fields
