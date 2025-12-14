#!/usr/bin/env python3
"""
Test script for FlowState MCP Server error handling and logging.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add scripts directory to path
sys.path.append('scripts')

def test_file_not_found():
    """Test error handling when correlations.json is missing"""
    print("Testing file not found error...")
    
    # Backup original file if it exists
    original_file = Path("public/correlations.json")
    backup_file = Path("public/correlations.json.test_backup")
    
    if original_file.exists():
        shutil.move(str(original_file), str(backup_file))
    
    try:
        from mcp_server import load_correlation_data
        try:
            load_correlation_data()
            print("❌ Expected MCPError but none was raised")
        except Exception as e:
            if "Correlation data not found" in str(e):
                print("✅ File not found error handled correctly")
            else:
                print(f"❌ Unexpected error: {e}")
    finally:
        # Restore original file
        if backup_file.exists():
            shutil.move(str(backup_file), str(original_file))

def test_json_parse_error():
    """Test error handling when JSON is corrupted"""
    print("Testing JSON parse error...")
    
    # Backup original file
    original_file = Path("public/correlations.json")
    backup_file = Path("public/correlations.json.test_backup")
    
    if original_file.exists():
        shutil.move(str(original_file), str(backup_file))
    
    try:
        # Create corrupted JSON file
        with open("public/correlations.json", "w") as f:
            f.write('{"invalid": "json", "missing": "bracket"')
        
        from mcp_server import load_correlation_data
        try:
            load_correlation_data()
            print("❌ Expected MCPError but none was raised")
        except Exception as e:
            if "Corrupted correlation data" in str(e):
                print("✅ JSON parse error handled correctly")
            else:
                print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up and restore
        if original_file.exists():
            original_file.unlink()
        if backup_file.exists():
            shutil.move(str(backup_file), str(original_file))

def test_missing_required_fields():
    """Test error handling when required fields are missing"""
    print("Testing missing required fields error...")
    
    # Backup original file
    original_file = Path("public/correlations.json")
    backup_file = Path("public/correlations.json.test_backup")
    
    if original_file.exists():
        shutil.move(str(original_file), str(backup_file))
    
    try:
        # Create JSON with missing required fields
        invalid_data = {
            "timeline": [],
            "totals": {},
            # Missing "correlations" and "insights"
        }
        
        with open("public/correlations.json", "w") as f:
            json.dump(invalid_data, f)
        
        from mcp_server import load_correlation_data
        try:
            load_correlation_data()
            print("❌ Expected MCPError but none was raised")
        except Exception as e:
            if "Missing required field" in str(e):
                print("✅ Missing required fields error handled correctly")
            else:
                print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up and restore
        if original_file.exists():
            original_file.unlink()
        if backup_file.exists():
            shutil.move(str(backup_file), str(original_file))

def test_invalid_parameters():
    """Test error handling for invalid tool parameters"""
    print("Testing invalid parameters...")
    
    from mcp_server import analyze_productivity, predict_commits
    
    # Test invalid date format
    result = analyze_productivity("invalid-date")
    if "error" in result and "Invalid date format" in result["error"]:
        print("✅ Invalid date format handled correctly")
    else:
        print(f"❌ Invalid date format not handled correctly: {result}")
    
    # Test negative parameters
    result = predict_commits(-1, -5)
    if "error" in result and "non-negative numbers" in result["error"]:
        print("✅ Negative parameters handled correctly")
    else:
        print(f"❌ Negative parameters not handled correctly: {result}")
    
    # Test invalid parameter types
    result = predict_commits("not_a_number", "also_not_a_number")
    if "error" in result and "numeric values" in result["error"]:
        print("✅ Invalid parameter types handled correctly")
    else:
        print(f"❌ Invalid parameter types not handled correctly: {result}")

def test_insufficient_data():
    """Test error handling when there's insufficient data"""
    print("Testing insufficient data scenarios...")
    
    # Backup original file
    original_file = Path("public/correlations.json")
    backup_file = Path("public/correlations.json.test_backup")
    
    if original_file.exists():
        shutil.move(str(original_file), str(backup_file))
    
    try:
        # Create minimal data that passes validation but is insufficient for analysis
        minimal_data = {
            "timeline": [
                {"date": "2024-01-01", "music_count": 0, "video_count": 0, "commit_count": 1}
            ],
            "totals": {"total_commits": 1, "total_music": 0, "total_videos": 0},
            "correlations": {
                "both": {"avg_commits": 0, "days": 0},
                "music_only": {"avg_commits": 0, "days": 0},
                "video_only": {"avg_commits": 0, "days": 0},
                "neither": {"avg_commits": 1, "days": 1}
            },
            "insights": {"best_pattern": "neither"}
        }
        
        with open("public/correlations.json", "w") as f:
            json.dump(minimal_data, f)
        
        from mcp_server import get_best_hours, get_flow_state_pattern
        
        # Test insufficient data for best hours
        result = get_best_hours()
        if "error" in result and "Insufficient data" in result["error"]:
            print("✅ Insufficient data for best hours handled correctly")
        else:
            print(f"❌ Insufficient data for best hours not handled correctly: {result}")
        
        # Test insufficient data for flow state pattern
        result = get_flow_state_pattern()
        if "error" in result and "Insufficient data" in result["error"]:
            print("✅ Insufficient data for flow state pattern handled correctly")
        else:
            print(f"❌ Insufficient data for flow state pattern not handled correctly: {result}")
            
    finally:
        # Clean up and restore
        if original_file.exists():
            original_file.unlink()
        if backup_file.exists():
            shutil.move(str(backup_file), str(original_file))

def main():
    """Run all error handling tests"""
    print("🧪 Testing FlowState MCP Server Error Handling\n")
    
    test_file_not_found()
    print()
    
    test_json_parse_error()
    print()
    
    test_missing_required_fields()
    print()
    
    test_invalid_parameters()
    print()
    
    test_insufficient_data()
    print()
    
    print("✅ All error handling tests completed!")

if __name__ == "__main__":
    main()