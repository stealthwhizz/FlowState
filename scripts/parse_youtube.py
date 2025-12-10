"""
Parse YouTube watch history from Google Takeout HTML export.

This script extracts video data from watch-history.html and outputs
a structured CSV with categorization and temporal fields.
"""

import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd


def categorize_video(title: str) -> str:
    """
    Categorize video as either "music" or "video" based on title keywords.
    
    Args:
        title: Video title string
        
    Returns:
        Category: "music" | "video"
    """
    title_lower = title.lower()
    
    # Enhanced music keywords - comprehensive music detection
    music_keywords = [
        # Direct music terms
        "music", "song", "beats", "lofi", "lo-fi", "synthwave", "playlist", "mix", "audio",
        "album", "track", "instrumental", "acoustic", "live music", "soundtrack", "ost",
        
        # Music video indicators
        "official music video", "official video", "music video", "mv", "lyrics", 
        "lyric video", "official audio", "full album", "ep", "single",
        
        # Genres
        "jazz", "classical", "hip hop", "rap", "edm", "electronic", "rock", "pop",
        "indie", "folk", "country", "r&b", "soul", "funk", "reggae", "blues",
        "metal", "punk", "alternative", "ambient", "chill", "downtempo",
        
        # Study/focus music
        "study music", "background music", "focus music", "relaxing", "meditation",
        "1 hour", "8 hour", "10 hours", "sleep music", "calm", "peaceful",
        
        # Music-related terms
        "remix", "cover", "acoustic version", "live performance", "concert",
        "studio session", "unplugged", "karaoke", "piano version", "guitar",
        "bass", "drums", "vocal", "singing", "singer", "artist", "band",
        
        # Common music video patterns
        "ft.", "feat.", "featuring", "vs.", "x ", " x ", "collab", "duet"
    ]
    
    # Check for music keywords (binary classification)
    if any(keyword in title_lower for keyword in music_keywords):
        return "music"
    
    # Everything else is categorized as "video"
    return "video"


def extract_datetime_fields(timestamp_str: str) -> dict:
    """
    Extract date, hour, and day_of_week from Google Takeout timestamp.
    
    Args:
        timestamp_str: Google Takeout timestamp string (e.g., "8 Dec 2025, 19:47:35 GMT+05:30")
        
    Returns:
        Dictionary with date, hour, day_of_week fields
    """
    try:
        import re
        
        # Clean up the timestamp string - remove extra text and normalize
        # Remove non-breaking spaces and other unicode characters
        timestamp_str = timestamp_str.replace('\xa0', ' ').replace('\u202f', ' ').strip()
        
        # Remove any "Watched" prefix and channel names that might be mixed in
        # Look for the GMT pattern and extract just the date/time part
        pattern = r'(\d{1,2}\s+\w{3}\s+\d{4},\s+\d{2}:\d{2}:\d{2})\s+GMT[+-]\d{2}:\d{2}'
        match = re.search(pattern, timestamp_str)
        
        if match:
            date_part = match.group(1)
            # Parse the date part: "8 Dec 2025, 19:47:35"
            dt = datetime.strptime(date_part, '%d %b %Y, %H:%M:%S')
            
            return {
                'date': dt.strftime('%Y-%m-%d'),
                'hour': dt.hour,
                'day_of_week': dt.strftime('%A')
            }
        else:
            # Fallback: try to find any date pattern in the string
            # Look for patterns like "26 Aug 2025, 10:32:56"
            date_pattern = r'(\d{1,2}\s+\w{3}\s+\d{4},\s+\d{2}:\d{2}:\d{2})'
            date_match = re.search(date_pattern, timestamp_str)
            
            if date_match:
                date_part = date_match.group(1)
                dt = datetime.strptime(date_part, '%d %b %Y, %H:%M:%S')
                
                return {
                    'date': dt.strftime('%Y-%m-%d'),
                    'hour': dt.hour,
                    'day_of_week': dt.strftime('%A')
                }
            else:
                print(f"Warning: No valid timestamp pattern found in: {timestamp_str[:100]}...")
                return {
                    'date': '',
                    'hour': 0,
                    'day_of_week': ''
                }
    except Exception as e:
        print(f"Warning: Failed to parse timestamp '{timestamp_str[:100]}...': {e}")
        return {
            'date': '',
            'hour': 0,
            'day_of_week': ''
        }


def parse_watch_history(html_path: str) -> pd.DataFrame:
    """
    Parse YouTube watch history HTML and return DataFrame.
    
    Args:
        html_path: Path to watch-history.html file
        
    Returns:
        DataFrame with columns: title, url, timestamp, date, hour, day_of_week, category
    """
    print(f"Reading HTML file: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("Parsing HTML content...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    videos = []
    skipped = 0
    
    # Find all content-cell divs that contain "Watched" text
    content_cells = soup.find_all('div', class_='content-cell')
    
    print(f"Found {len(content_cells)} content cells")
    
    for cell in content_cells:
        try:
            # Look for cells that contain "Watched" text
            cell_text = cell.get_text()
            if 'Watched' not in cell_text:
                continue
            
            # Find the video link (first link that goes to youtube.com/watch)
            links = cell.find_all('a', href=True)
            video_link = None
            
            for link in links:
                href = link.get('href', '')
                if 'youtube.com/watch' in href:
                    video_link = link
                    break
            
            if not video_link:
                skipped += 1
                continue
            
            # Extract title and URL
            title = video_link.get_text(strip=True)
            url = video_link.get('href', '')
            
            # Extract timestamp from the cell HTML - improved approach
            timestamp = ''
            cell_html = str(cell)
            import re
            
            # The HTML structure is: Watched <a>TITLE</a><br><a>CHANNEL</a><br>TIMESTAMP<br>
            # Look for timestamp pattern: DD MMM YYYY, HH:MM:SS GMT+XX:XX
            timestamp_pattern = r'(\d{1,2}\s+\w{3}\s+\d{4},\s+\d{2}:\d{2}:\d{2}\s+GMT[+-]\d{2}:\d{2})'
            
            # Method 1: Direct regex search in HTML
            timestamp_match = re.search(timestamp_pattern, cell_html)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
            else:
                # Method 2: Split by <br> and look for timestamp in each part
                br_parts = cell_html.split('<br>')
                for part in br_parts:
                    # Remove HTML tags and get clean text
                    part_soup = BeautifulSoup(part, 'html.parser')
                    part_text = part_soup.get_text().strip()
                    
                    # Clean up unicode characters
                    part_text = part_text.replace('\xa0', ' ').replace('\u202f', ' ').replace('\u200b', '')
                    
                    # Check if this part contains a timestamp
                    if re.search(timestamp_pattern, part_text):
                        timestamp_match = re.search(timestamp_pattern, part_text)
                        if timestamp_match:
                            timestamp = timestamp_match.group(1)
                            break
                    
                    # Also check for simpler patterns that might be malformed
                    if ('GMT' in part_text and ',' in part_text and 
                        any(char.isdigit() for char in part_text) and
                        len(part_text) > 10 and len(part_text) < 50):
                        # This looks like a timestamp, try to clean it up
                        timestamp = part_text.strip()
                        break
            
            if not timestamp:
                # Method 3: Look in the cell text directly
                cell_text_clean = cell_text.replace('\xa0', ' ').replace('\u202f', ' ').replace('\u200b', '')
                
                # Try to find timestamp in the text
                timestamp_match = re.search(timestamp_pattern, cell_text_clean)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                else:
                    # Look for any line that looks like a timestamp
                    lines = cell_text_clean.split('\n')
                    for line in lines:
                        line = line.strip()
                        if ('GMT' in line and ',' in line and 
                            any(char.isdigit() for char in line) and
                            len(line) > 10 and len(line) < 100):
                            timestamp = line
                            break
            
            if not timestamp:
                print(f"Warning: No timestamp found for video: {title}")
                skipped += 1
                continue
            
            # Extract datetime fields
            dt_fields = extract_datetime_fields(timestamp)
            
            # Skip if date parsing failed
            if not dt_fields['date']:
                print(f"Warning: Failed to parse date for video: {title}")
                skipped += 1
                continue
            
            # Categorize video
            category = categorize_video(title)
            
            videos.append({
                'title': title,
                'url': url,
                'timestamp': timestamp,
                'date': dt_fields['date'],
                'hour': dt_fields['hour'],
                'day_of_week': dt_fields['day_of_week'],
                'category': category
            })
            
        except Exception as e:
            print(f"Warning: Skipping entry due to error: {e}")
            skipped += 1
            continue
    
    print(f"Successfully parsed {len(videos)} videos")
    if skipped > 0:
        print(f"Skipped {skipped} entries due to errors or missing data")
    
    return pd.DataFrame(videos)


def main():
    """Main execution function."""
    try:
        # Check command line arguments
        if len(sys.argv) < 2:
            print("Usage: python parse_youtube.py <path_to_watch-history.html>")
            sys.exit(1)
        
        html_path = sys.argv[1]
        
        # Verify input file exists
        if not os.path.exists(html_path):
            print(f"Error: File not found: {html_path}")
            sys.exit(1)
        
        print("=" * 60)
        print("YouTube Watch History Parser")
        print("=" * 60)
        
        # Parse the HTML
        df = parse_watch_history(html_path)
        
        if df.empty:
            print("Warning: No videos were extracted from the HTML file")
            print("Please verify the file format matches Google Takeout export")
            sys.exit(1)
        
        # Create output directory if it doesn't exist
        output_dir = 'data'
        if not os.path.exists(output_dir):
            print(f"Creating directory: {output_dir}/")
            os.makedirs(output_dir)
        
        # Output CSV
        output_path = os.path.join(output_dir, 'youtube_data.csv')
        print(f"Writing CSV to: {output_path}")
        df.to_csv(output_path, index=False)
        
        print("=" * 60)
        print("Summary:")
        print(f"  Total videos: {len(df)}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"\nCategory breakdown:")
        for category, count in df['category'].value_counts().items():
            print(f"    {category}: {count}")
        print("=" * 60)
        print("✓ Successfully completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
