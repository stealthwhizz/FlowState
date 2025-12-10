#!/usr/bin/env python3
"""
Fetch GitHub commit history for a user and export to CSV.

Usage:
    python scripts/fetch_github.py <username>
    
Environment Variables:
    GITHUB_TOKEN: Optional GitHub personal access token for authentication
"""

import os
import sys
import time
import csv
from datetime import datetime
from typing import List, Dict, Optional
import requests


def fetch_user_repos(username: str, token: Optional[str]) -> List[Dict]:
    """Fetch repository list for user."""
    url = f"https://api.github.com/users/{username}/repos"
    headers = {}
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    print(f"Fetching repositories for user: {username}")
    
    try:
        response = requests.get(url, headers=headers, params={"per_page": 100})
        
        if response.status_code == 404:
            print(f"Error: User '{username}' not found (404)")
            return []
        elif response.status_code == 403:
            print(f"Error: Access forbidden (403). You may have hit rate limits.")
            return []
        elif response.status_code != 200:
            print(f"Error: Unexpected status code {response.status_code}")
            return []
        
        repos = response.json()
        print(f"Found {len(repos)} repositories")
        return repos[:20]  # Limit to 20 repositories
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching repositories: {e}")
        return []


def fetch_repo_commits(username: str, repo: str, token: Optional[str], limit: int = 100) -> List[Dict]:
    """Fetch commits for a specific repository."""
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    headers = {}
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, params={"per_page": limit})
        
        if response.status_code == 404:
            print(f"  Warning: Repository '{repo}' not found (404), skipping")
            return []
        elif response.status_code == 403:
            print(f"  Warning: Access forbidden for '{repo}' (403), skipping")
            return []
        elif response.status_code != 200:
            print(f"  Warning: Unexpected status code {response.status_code} for '{repo}', skipping")
            return []
        
        commits = response.json()
        return commits
        
    except requests.exceptions.RequestException as e:
        print(f"  Network error fetching commits for '{repo}': {e}, skipping")
        return []


def extract_commit_data(commit: Dict, repo_name: str) -> Dict:
    """Extract relevant fields from commit object."""
    try:
        # Get timestamp from commit
        timestamp_str = commit["commit"]["author"]["date"]
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        
        # Extract fields
        message = commit["commit"]["message"].split("\n")[0]  # First line only
        date = timestamp.strftime("%Y-%m-%d")
        hour = timestamp.hour
        day_of_week = timestamp.strftime("%A")
        
        return {
            "repo": repo_name,
            "message": message,
            "timestamp": timestamp_str,
            "date": date,
            "hour": hour,
            "day_of_week": day_of_week
        }
    except (KeyError, ValueError) as e:
        print(f"  Warning: Error extracting commit data: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_github.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    token = os.environ.get("GITHUB_TOKEN")
    
    if token:
        print("Using GITHUB_TOKEN for authentication")
    else:
        print("No GITHUB_TOKEN found, using unauthenticated requests (rate limit: 60/hour)")
    
    # Fetch repositories
    repos = fetch_user_repos(username, token)
    
    if not repos:
        print("No repositories found or error occurred")
        sys.exit(1)
    
    # Fetch commits from each repository
    all_commits = []
    
    for i, repo in enumerate(repos, 1):
        repo_name = repo["name"]
        print(f"[{i}/{len(repos)}] Fetching commits from: {repo_name}")
        
        commits = fetch_repo_commits(username, repo_name, token, limit=100)
        
        for commit in commits:
            commit_data = extract_commit_data(commit, repo_name)
            if commit_data:
                all_commits.append(commit_data)
        
        print(f"  Extracted {len(commits)} commits")
        
        # Add delay between requests to respect rate limiting
        if i < len(repos):  # Don't delay after the last repo
            time.sleep(1)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Write to CSV
    output_path = "data/github_data.csv"
    
    if all_commits:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["repo", "message", "timestamp", "date", "hour", "day_of_week"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_commits)
        
        print(f"\n✓ Successfully wrote {len(all_commits)} commits to {output_path}")
    else:
        print("\nNo commits found to write")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
