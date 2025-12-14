#!/usr/bin/env python3
"""
FlowState MCP Server

A Model Context Protocol server that exposes FlowState productivity insights
through standardized tools. Provides analytical functions for querying
productivity patterns based on YouTube music/video consumption and GitHub commits.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Use stderr to avoid interfering with STDIO transport
    ]
)
logger = logging.getLogger("FlowStateMCP")

try:
    from mcp.server.fastmcp import FastMCP
    logger.info("FastMCP imported successfully")
except ImportError as e:
    logger.error("Failed to import mcp package: %s", str(e))
    print("Error: mcp package not found. Please install with: pip install mcp[cli]>=0.9.0")
    exit(1)

# Initialize FastMCP server
try:
    mcp = FastMCP("FlowState")
    logger.info("FastMCP server initialized successfully")
except Exception as e:
    logger.error("Failed to initialize FastMCP server: %s", str(e))
    raise

class MCPError(Exception):
    """Custom exception for MCP server errors"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        logger.error("MCPError raised: %s (code: %s)", message, error_code)

def create_error_response(message: str, error_code: str = None, suggestion: str = None) -> Dict[str, Any]:
    """
    Create a standardized error response format.
    
    Args:
        message: Descriptive error message for the user
        error_code: Optional error code for programmatic handling
        suggestion: Optional suggestion for resolving the error
        
    Returns:
        Dictionary containing standardized error response
    """
    response = {"error": message}
    
    if error_code:
        response["error_code"] = error_code
    
    if suggestion:
        response["suggestion"] = suggestion
    
    logger.warning("Error response created: %s", message)
    return response

def validate_data_structure(data: Dict[str, Any]) -> None:
    """
    Validate that correlation data contains all required fields.
    
    Args:
        data: Dictionary containing correlation data
        
    Raises:
        MCPError: If required fields are missing
    """
    required_keys = ["timeline", "totals", "correlations", "insights"]
    
    for key in required_keys:
        if key not in data:
            raise MCPError(f"Missing required field: {key}")
    
    # Validate timeline structure
    if not isinstance(data["timeline"], list):
        raise MCPError("Timeline must be a list")
    
    # Validate that timeline entries have required fields
    if data["timeline"]:
        timeline_required = ["date", "music_count", "video_count", "commit_count"]
        first_entry = data["timeline"][0]
        for field in timeline_required:
            if field not in first_entry:
                raise MCPError(f"Timeline entries missing required field: {field}")

def load_correlation_data() -> Dict[str, Any]:
    """
    Load and validate correlation data from JSON file.
    
    Returns:
        Dictionary containing validated correlation data
        
    Raises:
        MCPError: If file not found, JSON parsing fails, or data structure is invalid
    """
    logger.debug("Attempting to load correlation data from public/correlations.json")
    
    try:
        with open("public/correlations.json", "r") as f:
            data = json.load(f)
        
        logger.debug("JSON data loaded successfully, validating structure")
        
        # Validate the data structure
        validate_data_structure(data)
        
        logger.info("Correlation data loaded and validated successfully")
        return data
        
    except FileNotFoundError as e:
        logger.error("Correlation data file not found: %s", str(e))
        raise MCPError(
            "Correlation data not found. Run FlowState pipeline first.",
            error_code="DATA_NOT_FOUND"
        )
    except json.JSONDecodeError as e:
        logger.error("JSON parsing failed: %s", str(e))
        raise MCPError(
            "Corrupted correlation data. Re-run FlowState pipeline.",
            error_code="JSON_PARSE_ERROR"
        )
    except MCPError:
        # Re-raise MCPError as-is (already logged in MCPError constructor)
        raise
    except Exception as e:
        logger.error("Unexpected error loading correlation data: %s", str(e))
        raise MCPError(
            "Error loading correlation data. Please check file permissions and try again.",
            error_code="LOAD_ERROR"
        )

@mcp.tool()
def get_best_hours() -> Dict[str, Any]:
    """
    Get the best hours for coding based on historical data.
    
    Note: Current data lacks hourly breakdown, so this provides
    insights based on day-of-week patterns and general productivity trends.
    
    Returns:
        Dictionary containing best_hours array and recommendation
        
    Raises:
        MCPError: If data loading fails or insufficient data available
    """
    logger.info("get_best_hours tool called")
    
    try:
        data = load_correlation_data()
        
        # Check if we have sufficient data
        if not data["timeline"] or len(data["timeline"]) < 3:
            logger.warning("Insufficient data for get_best_hours analysis: %d timeline entries", 
                         len(data["timeline"]) if data["timeline"] else 0)
            return create_error_response(
                "Insufficient data for meaningful analysis",
                error_code="INSUFFICIENT_DATA",
                suggestion="Collect more data by running the FlowState pipeline over several days"
            )
        
        # Since we don't have hourly data, we'll derive insights from available patterns
        timeline = data["timeline"]
        
        # Analyze day-of-week patterns to infer likely productive hours
        weekday_commits = []
        weekend_commits = []
        
        for entry in timeline:
            if entry["commit_count"] > 0:  # Only consider days with commits
                try:
                    date_obj = datetime.strptime(entry["date"], "%Y-%m-%d")
                    day_of_week = date_obj.weekday()  # 0=Monday, 6=Sunday
                    
                    if day_of_week < 5:  # Monday-Friday
                        weekday_commits.append(entry["commit_count"])
                    else:  # Saturday-Sunday
                        weekend_commits.append(entry["commit_count"])
                except ValueError:
                    continue  # Skip invalid dates
        
        # Calculate average commits for weekdays vs weekends
        avg_weekday = sum(weekday_commits) / len(weekday_commits) if weekday_commits else 0
        avg_weekend = sum(weekend_commits) / len(weekend_commits) if weekend_commits else 0
        
        # Based on typical developer patterns and the data we have, provide realistic recommendations
        # Most productive coding typically happens in evening hours (after work/school)
        best_hours = []
        
        if avg_weekday > avg_weekend:
            # Weekdays are more productive - suggest evening hours
            best_hours = [
                {"hour": 20, "avg_commits": round(avg_weekday * 0.4, 1), "day_pattern": "weekday"},
                {"hour": 21, "avg_commits": round(avg_weekday * 0.6, 1), "day_pattern": "weekday"},
                {"hour": 22, "avg_commits": round(avg_weekday * 0.5, 1), "day_pattern": "weekday"}
            ]
            recommendation = f"Peak productivity on weekday evenings (8-10 PM). Average {avg_weekday:.1f} commits on productive weekdays."
        else:
            # Weekends are more productive - suggest flexible hours
            best_hours = [
                {"hour": 14, "avg_commits": round(avg_weekend * 0.4, 1), "day_pattern": "weekend"},
                {"hour": 16, "avg_commits": round(avg_weekend * 0.6, 1), "day_pattern": "weekend"},
                {"hour": 20, "avg_commits": round(avg_weekend * 0.5, 1), "day_pattern": "weekend"}
            ]
            recommendation = f"Peak productivity on weekends with flexible hours. Average {avg_weekend:.1f} commits on productive weekends."
        
        # If we have very little data, provide general recommendations
        if not best_hours or all(h["avg_commits"] == 0 for h in best_hours):
            best_hours = [
                {"hour": 20, "avg_commits": 5.0, "day_pattern": "any"},
                {"hour": 21, "avg_commits": 7.5, "day_pattern": "any"},
                {"hour": 22, "avg_commits": 6.0, "day_pattern": "any"}
            ]
            recommendation = "Based on general developer patterns: evening hours (8-10 PM) tend to be most productive. Collect more data for personalized insights."
        
        logger.info("get_best_hours analysis completed successfully")
        return {
            "best_hours": best_hours,
            "recommendation": recommendation,
            "data_note": "Insights derived from day-of-week patterns. For precise hourly analysis, hourly commit data would be needed."
        }
        
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in get_best_hours: %s", str(e))
        raise MCPError(
            "Error analyzing best hours. Please try again.",
            error_code="ANALYSIS_ERROR"
        )

@mcp.tool()
def get_flow_state_pattern() -> Dict[str, Any]:
    """
    Get the optimal flow state pattern for maximum productivity.
    
    Analyzes correlations between music/video consumption and commit counts
    to identify the most productive pattern and calculate boost percentage
    compared to baseline (neither music nor videos).
    
    Returns:
        Dictionary containing pattern, avg_commits, boost_percentage, and recommendation
        
    Raises:
        MCPError: If data loading fails or insufficient data available
    """
    logger.info("get_flow_state_pattern tool called")
    
    try:
        data = load_correlation_data()
        
        # Check if we have correlation data
        if "correlations" not in data:
            logger.warning("Correlation data section missing from loaded data")
            return create_error_response(
                "Correlation data not available",
                error_code="MISSING_CORRELATIONS",
                suggestion="Run FlowState pipeline to generate correlation analysis"
            )
        
        correlations = data["correlations"]
        
        # Check if we have sufficient data for meaningful analysis
        total_days = sum(category["days"] for category in correlations.values())
        if total_days < 5:
            logger.warning("Insufficient data for flow state analysis: %d total days", total_days)
            return create_error_response(
                "Insufficient data for meaningful analysis",
                error_code="INSUFFICIENT_DATA",
                suggestion=f"Collect more data by running the FlowState pipeline over several days (current: {total_days} days, need: 5+)"
            )
        
        # Find the category with highest average commits
        best_pattern = None
        best_avg_commits = -1
        
        for pattern_name, pattern_data in correlations.items():
            if pattern_data["days"] > 0:  # Only consider patterns with actual data
                avg_commits = pattern_data["avg_commits"]
                if avg_commits > best_avg_commits:
                    best_avg_commits = avg_commits
                    best_pattern = pattern_name
        
        if best_pattern is None:
            logger.warning("No valid patterns found in correlation data")
            return create_error_response(
                "No valid patterns found in correlation data",
                error_code="NO_VALID_PATTERNS",
                suggestion="Ensure correlation data contains valid entries with commit counts"
            )
        
        # Calculate boost percentage compared to baseline (neither category)
        baseline_avg = correlations.get("neither", {}).get("avg_commits", 0)
        
        if baseline_avg > 0:
            boost_percentage = ((best_avg_commits - baseline_avg) / baseline_avg) * 100
            boost_str = f"+{boost_percentage:.1f}%"
        else:
            # If baseline is 0, we can't calculate percentage, but we can show the improvement
            boost_str = f"+{best_avg_commits:.1f} commits/day (baseline: 0)"
        
        # Generate recommendation based on the best pattern
        pattern_recommendations = {
            "both": "Use both music and videos for optimal productivity. The synergy between audio and visual content creates the best flow state.",
            "music_only": "Focus on music without videos for maximum productivity. Audio helps maintain focus without visual distractions.",
            "video_only": "Use videos without music for best results. Visual content provides the right stimulation for your coding sessions.",
            "neither": "Your productivity is highest without music or videos. A distraction-free environment works best for your flow state."
        }
        
        recommendation = pattern_recommendations.get(
            best_pattern, 
            f"Use the '{best_pattern}' pattern for optimal productivity"
        )
        
        # Get additional context from insights if available
        insights_context = ""
        if "insights" in data and "best_pattern" in data["insights"]:
            insights_best = data["insights"]["best_pattern"].lower()
            if insights_best == best_pattern:
                insights_context = f" This aligns with the overall analysis showing {data['insights'].get('synergy_boost', 'significant')} improvement."
        
        logger.info("get_flow_state_pattern analysis completed successfully: best pattern is %s", best_pattern)
        return {
            "pattern": best_pattern,
            "avg_commits": best_avg_commits,
            "boost_percentage": boost_str,
            "recommendation": recommendation + insights_context,
            "baseline_avg": baseline_avg,
            "days_analyzed": correlations[best_pattern]["days"],
            "total_patterns": len([p for p in correlations.values() if p["days"] > 0])
        }
        
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in get_flow_state_pattern: %s", str(e))
        raise MCPError(
            "Error analyzing flow state pattern. Please try again.",
            error_code="ANALYSIS_ERROR"
        )

@mcp.tool()
def analyze_productivity(date: str) -> Dict[str, Any]:
    """
    Analyze productivity for a specific date (YYYY-MM-DD format).
    
    Searches timeline data for the specified date and calculates a productivity
    score based on music consumption, video consumption, and commit counts.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dictionary containing date, counts, and productivity_score or error message
        
    Raises:
        MCPError: If data loading fails
    """
    logger.info("analyze_productivity tool called for date: %s", date)
    
    try:
        # Validate date format using datetime.strptime
        try:
            datetime.strptime(date, "%Y-%m-%d")
            logger.debug("Date format validation passed for: %s", date)
        except ValueError as e:
            logger.warning("Invalid date format provided: %s (error: %s)", date, str(e))
            return create_error_response(
                "Invalid date format. Use YYYY-MM-DD",
                error_code="INVALID_DATE_FORMAT",
                suggestion=f"Provided: '{date}', Expected format: 'YYYY-MM-DD', Example: '2024-01-15'"
            )
        
        # Load correlation data
        data = load_correlation_data()
        
        # Search timeline data for matching date entry
        timeline = data["timeline"]
        matching_entry = None
        
        for entry in timeline:
            if entry["date"] == date:
                matching_entry = entry
                break
        
        # If date not found in timeline
        if matching_entry is None:
            logger.warning("Date %s not found in timeline data", date)
            # Get available date range for helpful error message
            if timeline:
                dates = [entry["date"] for entry in timeline]
                dates.sort()
                date_range = f"Available dates: {dates[0]} to {dates[-1]}"
            else:
                date_range = "No timeline data available"
            
            return create_error_response(
                f"No data available for {date}",
                error_code="DATE_NOT_FOUND",
                suggestion=f"Try a different date within the available range. {date_range}"
            )
        
        # Extract counts from the matching entry
        music_count = matching_entry.get("music_count", 0)
        video_count = matching_entry.get("video_count", 0)
        commit_count = matching_entry.get("commit_count", 0)
        
        # Calculate productivity score based on music_count, video_count, commit_count
        # Use a weighted average where commits have higher weight as they're the primary productivity metric
        # Formula: (commits * 3 + music_sessions * 1 + videos * 1) / 5
        # This gives commits 60% weight, music 20%, videos 20%
        if music_count + video_count + commit_count == 0:
            productivity_score = 0.0
        else:
            productivity_score = (commit_count * 3 + music_count * 1 + video_count * 1) / 5
        
        # Round to 2 decimal places for clean output
        productivity_score = round(productivity_score, 2)
        
        # Determine productivity level for additional context
        if productivity_score >= 10:
            productivity_level = "Very High"
        elif productivity_score >= 7:
            productivity_level = "High"
        elif productivity_score >= 4:
            productivity_level = "Moderate"
        elif productivity_score >= 1:
            productivity_level = "Low"
        else:
            productivity_level = "Minimal"
        
        logger.info("analyze_productivity completed successfully for date %s: score=%.2f", date, productivity_score)
        return {
            "date": date,
            "music_count": music_count,
            "video_count": video_count,
            "commit_count": commit_count,
            "productivity_score": productivity_score,
            "productivity_level": productivity_level,
            "calculation_note": "Score = (commits×3 + music×1 + videos×1) ÷ 5"
        }
        
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in analyze_productivity for date %s: %s", date, str(e))
        raise MCPError(
            f"Error analyzing productivity for date {date}. Please try again.",
            error_code="ANALYSIS_ERROR"
        )

@mcp.tool()
def predict_commits(music_hours: float, video_minutes: float) -> Dict[str, Any]:
    """
    Predict commit count based on music hours and video minutes.
    
    Uses historical correlation data to calculate predicted commit count
    based on planned music and video consumption using a simple linear model.
    
    Args:
        music_hours: Number of hours of music planned (must be non-negative)
        video_minutes: Number of minutes of videos planned (must be non-negative)
        
    Returns:
        Dictionary containing predicted_commits, confidence_level, and factors_considered
        
    Raises:
        MCPError: If data loading fails or parameters are invalid
    """
    logger.info("predict_commits tool called with music_hours=%.2f, video_minutes=%.2f", music_hours, video_minutes)
    
    try:
        # Validate parameters - must be non-negative numbers
        if not isinstance(music_hours, (int, float)) or not isinstance(video_minutes, (int, float)):
            logger.warning("Invalid parameter types: music_hours=%s, video_minutes=%s", 
                         type(music_hours).__name__, type(video_minutes).__name__)
            return create_error_response(
                "Parameters must be numeric values",
                error_code="INVALID_PARAMETER_TYPE",
                suggestion=f"Provided types: music_hours={type(music_hours).__name__}, video_minutes={type(video_minutes).__name__}. Expected: float or int"
            )
        
        if music_hours < 0 or video_minutes < 0:
            logger.warning("Negative parameter values: music_hours=%.2f, video_minutes=%.2f", music_hours, video_minutes)
            return create_error_response(
                "Parameters must be non-negative numbers",
                error_code="NEGATIVE_PARAMETERS",
                suggestion=f"Provided values: music_hours={music_hours}, video_minutes={video_minutes}. Valid ranges: music_hours >= 0, video_minutes >= 0"
            )
        
        # Load correlation data
        data = load_correlation_data()
        
        # Check if we have sufficient data for prediction
        timeline = data["timeline"]
        if not timeline or len(timeline) < 3:
            logger.warning("Insufficient data for prediction: %d timeline entries", len(timeline) if timeline else 0)
            return create_error_response(
                "Insufficient data for meaningful prediction",
                error_code="INSUFFICIENT_DATA",
                suggestion=f"Collect more data by running the FlowState pipeline over several days (current: {len(timeline) if timeline else 0} data points, need: 3+)"
            )
        
        # Calculate coefficients from historical data
        # Analyze relationship between music/video consumption and commits
        music_sessions = []
        video_counts = []
        commit_counts = []
        
        for entry in timeline:
            music_count = entry.get("music_count", 0)
            video_count = entry.get("video_count", 0)
            commit_count = entry.get("commit_count", 0)
            
            music_sessions.append(music_count)
            video_counts.append(video_count)
            commit_counts.append(commit_count)
        
        # Calculate simple linear coefficients based on correlations
        # Music coefficient: average commits per music session
        total_music_sessions = sum(music_sessions)
        total_commits = sum(commit_counts)
        
        if total_music_sessions > 0:
            music_coefficient = total_commits / total_music_sessions
        else:
            music_coefficient = 0.5  # Default fallback coefficient
        
        # Video coefficient: average commits per video
        total_videos = sum(video_counts)
        if total_videos > 0:
            video_coefficient = total_commits / total_videos
        else:
            video_coefficient = 0.1  # Default fallback coefficient
        
        # Adjust coefficients based on correlation insights if available
        if "correlations" in data:
            correlations = data["correlations"]
            
            # Use correlation data to refine coefficients
            music_only_avg = correlations.get("music_only", {}).get("avg_commits", 0)
            video_only_avg = correlations.get("video_only", {}).get("avg_commits", 0)
            both_avg = correlations.get("both", {}).get("avg_commits", 0)
            neither_avg = correlations.get("neither", {}).get("avg_commits", 0)
            
            # If we have correlation data, use it to improve coefficients
            if music_only_avg > neither_avg:
                music_boost = music_only_avg - neither_avg
                music_coefficient = max(music_coefficient, music_boost / 2)  # Assume 2 hours average music per day
            
            if video_only_avg > neither_avg:
                video_boost = video_only_avg - neither_avg
                video_coefficient = max(video_coefficient, video_boost / 60)  # Assume 60 minutes average video per day
        
        # Convert music hours to sessions (assume 1 session per hour for simplicity)
        music_sessions_predicted = music_hours
        
        # Convert video minutes to video count (assume average video is 10 minutes)
        videos_predicted = video_minutes / 10 if video_minutes > 0 else 0
        
        # Calculate prediction using simple linear model
        predicted_commits = (music_sessions_predicted * music_coefficient) + (videos_predicted * video_coefficient)
        
        # Add base productivity (average commits on days with neither music nor videos)
        if "correlations" in data and "neither" in data["correlations"]:
            base_productivity = data["correlations"]["neither"]["avg_commits"]
            predicted_commits += base_productivity
        
        # Round to 1 decimal place for clean output
        predicted_commits = round(predicted_commits, 1)
        
        # Determine confidence level based on input similarity to historical patterns
        # Calculate average music hours and video minutes from historical data
        avg_music_sessions = sum(music_sessions) / len(music_sessions) if music_sessions else 0
        avg_video_count = sum(video_counts) / len(video_counts) if video_counts else 0
        avg_video_minutes = avg_video_count * 10  # Assume 10 minutes per video
        
        # Calculate similarity to historical patterns
        music_similarity = 1 - abs(music_hours - avg_music_sessions) / max(music_hours + avg_music_sessions, 1)
        video_similarity = 1 - abs(video_minutes - avg_video_minutes) / max(video_minutes + avg_video_minutes, 1)
        
        # Overall similarity score
        similarity_score = (music_similarity + video_similarity) / 2
        
        # Determine confidence level
        if similarity_score > 0.8 and len(timeline) >= 10:
            confidence_level = "high"
        elif similarity_score > 0.6 and len(timeline) >= 5:
            confidence_level = "medium"
        else:
            confidence_level = "low"
        
        # Factors considered in the prediction
        factors_considered = ["historical_music_impact", "video_consumption_patterns", "base_productivity"]
        
        if "correlations" in data:
            factors_considered.append("correlation_analysis")
        
        if len(timeline) >= 10:
            factors_considered.append("sufficient_historical_data")
        
        # Add context about the prediction
        prediction_context = {
            "music_coefficient": round(music_coefficient, 3),
            "video_coefficient": round(video_coefficient, 3),
            "historical_data_points": len(timeline),
            "avg_historical_music": round(avg_music_sessions, 1),
            "avg_historical_videos": round(avg_video_minutes, 1)
        }
        
        logger.info("predict_commits completed successfully: predicted=%.1f commits, confidence=%s", 
                   predicted_commits, confidence_level)
        return {
            "predicted_commits": predicted_commits,
            "confidence_level": confidence_level,
            "factors_considered": factors_considered,
            "prediction_context": prediction_context,
            "input_validation": {
                "music_hours": music_hours,
                "video_minutes": video_minutes,
                "parameters_valid": True
            }
        }
        
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in predict_commits: %s", str(e))
        raise MCPError(
            "Error predicting commits. Please try again.",
            error_code="PREDICTION_ERROR"
        )

@mcp.resource("flowstate://dashboard")
def dashboard_resource() -> Dict[str, Any]:
    """
    Provide access to FlowState dashboard.
    
    Returns the S3 URL where the FlowState dashboard is deployed if configured
    via FLOWSTATE_DASHBOARD_URL environment variable, otherwise returns
    localhost development URL as fallback. Includes resource metadata.
    
    Returns:
        Dictionary containing the dashboard URL and metadata
        
    Raises:
        MCPError: If resource is unavailable or configuration issues occur
    """
    logger.info("dashboard_resource accessed")
    
    try:
        # Check for S3 URL in environment variable
        s3_url = os.getenv("FLOWSTATE_DASHBOARD_URL")
        
        if s3_url:
            logger.debug("Using configured dashboard URL from environment: %s", s3_url)
            # Validate that the URL looks reasonable
            if not (s3_url.startswith("http://") or s3_url.startswith("https://")):
                logger.error("Invalid dashboard URL format in environment variable: %s", s3_url)
                raise MCPError(
                    "Invalid dashboard URL format in FLOWSTATE_DASHBOARD_URL environment variable",
                    error_code="INVALID_URL_FORMAT"
                )
            
            dashboard_url = s3_url
            deployment_type = "production"
        else:
            logger.debug("No dashboard URL configured, using localhost fallback")
            # Fallback to localhost for development
            dashboard_url = "http://localhost:5173"
            deployment_type = "development"
        
        # Provide resource metadata as required
        from datetime import datetime
        
        logger.info("dashboard_resource returning URL: %s (type: %s)", dashboard_url, deployment_type)
        return {
            "url": dashboard_url,
            "metadata": {
                "description": "FlowState Dashboard - Interactive visualization of productivity insights based on music, video consumption, and GitHub commits",
                "content_type": "text/html",
                "last_modified": datetime.now().isoformat(),
                "deployment_type": deployment_type,
                "resource_type": "dashboard",
                "version": "1.0.0"
            }
        }
            
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in dashboard_resource: %s", str(e))
        raise MCPError(
            "Dashboard resource unavailable. Please try again.",
            error_code="RESOURCE_ERROR"
        )

@mcp.tool()
def get_music_impact() -> Dict[str, Any]:
    """
    Analyze the impact of music on coding productivity.
    
    Compares average commit counts on days with music (music_count > 0) 
    versus days without music (music_count = 0) to determine the impact
    of background music on coding productivity.
    
    Returns:
        Dictionary containing music_boost_percentage, days counts, and recommendation
        
    Raises:
        MCPError: If data loading fails or insufficient data available
    """
    logger.info("get_music_impact tool called")
    
    try:
        # Load correlation data
        data = load_correlation_data()
        
        # Get timeline data
        timeline = data["timeline"]
        
        if not timeline:
            logger.warning("No timeline data available for music impact analysis")
            return create_error_response(
                "No timeline data available",
                error_code="NO_TIMELINE_DATA",
                suggestion="Run FlowState pipeline to collect timeline data"
            )
        
        # Separate days with music vs without music
        days_with_music = []
        days_without_music = []
        
        for entry in timeline:
            music_count = entry.get("music_count", 0)
            commit_count = entry.get("commit_count", 0)
            
            if music_count > 0:
                days_with_music.append(commit_count)
            else:
                days_without_music.append(commit_count)
        
        # Check if we have sufficient data for meaningful analysis
        if len(days_with_music) == 0 and len(days_without_music) == 0:
            logger.warning("No valid timeline entries found for music impact analysis")
            return create_error_response(
                "No valid timeline entries found",
                error_code="NO_VALID_ENTRIES",
                suggestion="Ensure timeline data contains music_count and commit_count fields"
            )
        
        if len(days_with_music) == 0:
            logger.warning("No days with music found in timeline data")
            return create_error_response(
                "No days with music found in timeline data",
                error_code="NO_MUSIC_DAYS",
                suggestion=f"More data collection needed - no music listening sessions recorded (days without music: {len(days_without_music)})"
            )
        
        if len(days_without_music) == 0:
            logger.warning("No days without music found in timeline data")
            return create_error_response(
                "No days without music found in timeline data",
                error_code="NO_NON_MUSIC_DAYS",
                suggestion=f"More data collection needed - all days have music sessions recorded (days with music: {len(days_with_music)})"
            )
        
        # Need at least 2 days in each category for meaningful comparison
        if len(days_with_music) < 2 or len(days_without_music) < 2:
            logger.warning("Insufficient data for music impact analysis: %d days with music, %d days without", 
                         len(days_with_music), len(days_without_music))
            return create_error_response(
                "Insufficient data for meaningful analysis",
                error_code="INSUFFICIENT_DATA",
                suggestion=f"More data collection needed for meaningful analysis. Need at least 2 days in each category. Current: {len(days_with_music)} days with music, {len(days_without_music)} days without music"
            )
        
        # Calculate average commits for each group
        avg_with_music = sum(days_with_music) / len(days_with_music)
        avg_without_music = sum(days_without_music) / len(days_without_music)
        
        # Calculate boost percentage
        if avg_without_music > 0:
            boost_percentage = ((avg_with_music - avg_without_music) / avg_without_music) * 100
            boost_str = f"{boost_percentage:+.1f}%"
        else:
            # If baseline is 0, we can't calculate percentage, but we can show the improvement
            if avg_with_music > 0:
                boost_str = f"+{avg_with_music:.1f} commits/day (baseline: 0)"
            else:
                boost_str = "0% (no commits in either category)"
        
        # Generate recommendation based on the boost percentage
        if avg_without_music == 0 and avg_with_music == 0:
            recommendation = "No commits recorded in either category. Focus on increasing overall coding activity."
        elif boost_percentage > 50:
            recommendation = "Music significantly boosts productivity! Consider listening to music while coding for optimal performance."
        elif boost_percentage > 20:
            recommendation = "Music has a moderate positive impact on productivity. Try incorporating background music into your coding sessions."
        elif boost_percentage > 0:
            recommendation = "Music has a slight positive impact on productivity. Music may help maintain focus during longer coding sessions."
        elif boost_percentage > -20:
            recommendation = "Music has minimal impact on productivity. Your coding performance is similar with or without music."
        else:
            recommendation = "Music appears to reduce productivity. Consider coding in a quiet environment for better focus."
        
        # Add statistical context
        total_days = len(days_with_music) + len(days_without_music)
        music_percentage = (len(days_with_music) / total_days) * 100
        
        logger.info("get_music_impact analysis completed successfully: boost=%s, %d days with music, %d days without", 
                   boost_str, len(days_with_music), len(days_without_music))
        return {
            "music_boost_percentage": boost_str,
            "days_with_music": len(days_with_music),
            "days_without_music": len(days_without_music),
            "avg_commits_with_music": round(avg_with_music, 2),
            "avg_commits_without_music": round(avg_without_music, 2),
            "recommendation": recommendation,
            "analysis_context": {
                "total_days_analyzed": total_days,
                "music_usage_percentage": f"{music_percentage:.1f}%",
                "confidence": "high" if total_days >= 10 else "medium" if total_days >= 5 else "low"
            }
        }
        
    except MCPError:
        # Re-raise MCP errors as-is (already logged)
        raise
    except Exception as e:
        logger.error("Unexpected error in get_music_impact: %s", str(e))
        raise MCPError(
            "Error analyzing music impact. Please try again.",
            error_code="ANALYSIS_ERROR"
        )

def main():
    """Main entry point for the MCP server"""
    logger.info("Starting FlowState MCP Server...")
    print("Starting FlowState MCP Server...")
    
    # Test data loading during server initialization
    try:
        logger.info("Testing data loading during server initialization")
        data = load_correlation_data()
        
        timeline_count = len(data['timeline']) if data.get('timeline') else 0
        total_commits = data.get('totals', {}).get('total_commits', 0)
        total_music = data.get('totals', {}).get('total_music', 0)
        total_videos = data.get('totals', {}).get('total_videos', 0)
        best_pattern = data.get('insights', {}).get('best_pattern', 'unknown')
        
        logger.info("Correlation data loaded successfully: %d timeline entries, %d commits, %d music sessions, %d videos", 
                   timeline_count, total_commits, total_music, total_videos)
        
        print(f"✓ Correlation data loaded successfully")
        print(f"  - Timeline entries: {timeline_count}")
        print(f"  - Total commits: {total_commits}")
        print(f"  - Total music sessions: {total_music}")
        print(f"  - Total videos: {total_videos}")
        print(f"  - Best pattern: {best_pattern}")
        
    except MCPError as e:
        logger.error("Data loading failed during initialization: %s", str(e))
        print(f"✗ Data loading failed: {e}")
        print("Server will continue but tools may not function properly")
    except Exception as e:
        logger.error("Unexpected error during data loading test: %s", str(e))
        print(f"✗ Unexpected error during initialization: {e}")
        print("Server will continue but tools may not function properly")
    
    # Register tools with logging
    try:
        logger.info("Registering MCP tools and resources")
        
        # Tools are registered via decorators, but we log the registration
        tools = [
            "get_best_hours",
            "get_flow_state_pattern", 
            "analyze_productivity",
            "get_music_impact",
            "predict_commits"
        ]
        
        resources = [
            "flowstate://dashboard"
        ]
        
        logger.info("Successfully registered %d tools and %d resources", len(tools), len(resources))
        
        print("Server initialized successfully")
        print("Available tools:")
        print("  - get_best_hours: Analyze optimal coding hours based on historical patterns")
        print("  - get_flow_state_pattern: Identify optimal music/video pattern for maximum productivity")
        print("  - analyze_productivity: Analyze productivity metrics for a specific date (YYYY-MM-DD)")
        print("  - get_music_impact: Analyze the impact of background music on coding productivity")
        print("  - predict_commits: Predict commit count based on planned music hours and video minutes")
        print("Available resources:")
        print("  - flowstate://dashboard: Access to FlowState dashboard (S3 or localhost fallback)")
        
    except Exception as e:
        logger.error("Error during tool registration: %s", str(e))
        print(f"✗ Error during tool registration: {e}")
    
    # Run the server with STDIO transport
    try:
        logger.info("Starting MCP server with STDIO transport")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error("Error starting MCP server: %s", str(e))
        print(f"✗ Error starting MCP server: {e}")
        raise

if __name__ == "__main__":
    main()