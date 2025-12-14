# Implementation Plan

- [x] 1. Set up MCP server dependencies and project structure





  - Add mcp[cli]>=0.9.0 to requirements.txt
  - Verify existing FlowState pipeline is functional and correlations.json exists
  - Create scripts/mcp_server.py file with basic FastMCP imports
  - Test that FastMCP can be imported and basic server can initialize
  - _Requirements: 8.1, 8.2_

- [x] 2. Implement core data loading and validation module





  - Create load_correlation_data() function to read public/correlations.json
  - Implement validate_data_structure() function to check required keys (timeline, totals, correlations, insights)
  - Add error handling for FileNotFoundError and JSONDecodeError with descriptive messages
  - Test data loading with existing correlations.json file
  - _Requirements: 1.1, 7.1, 7.2_

- [ ]* 2.1 Write property test for data loading consistency
  - **Property 1: Data loading consistency**
  - **Validates: Requirements 1.1**

- [x] 3. Implement get_best_hours() MCP tool





  - Register get_best_hours tool with FastMCP using @mcp.tool() decorator
  - Implement function to analyze timeline data for hourly patterns (note: current data lacks hourly breakdown, use placeholder logic)
  - Return JSON response with best_hours array containing hour, avg_commits, day_pattern fields
  - Add error handling for missing or insufficient data
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 3.1 Write property test for maximum value identification
  - **Property 2: Maximum value identification consistency**
  - **Validates: Requirements 1.2**

- [ ]* 3.2 Write property test for JSON response structure
  - **Property 3: JSON response structure consistency**
  - **Validates: Requirements 1.3**

- [x] 4. Implement get_flow_state_pattern() MCP tool









  - Register get_flow_state_pattern tool with FastMCP
  - Analyze correlations data to find category with highest avg_commits
  - Calculate boost percentage compared to baseline (neither category)
  - Return JSON response with pattern, avg_commits, boost_percentage, recommendation fields
  - Handle edge case when insufficient data exists
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 4.1 Write property test for mathematical calculations
  - **Property 4: Mathematical calculation consistency**
  - **Validates: Requirements 2.3**

- [x] 5. Implement analyze_productivity(date) MCP tool




  - Register analyze_productivity tool with FastMCP, accepting date parameter
  - Implement date format validation for YYYY-MM-DD format using datetime.strptime
  - Search timeline data for matching date entry
  - Calculate productivity score based on music_count, video_count, commit_count
  - Return JSON response with date, counts, and productivity_score or error message
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 5.1 Write property test for date validation
  - **Property 5: Date validation consistency**
  - **Validates: Requirements 3.1**

- [ ]* 5.2 Write property test for timeline search
  - **Property 6: Timeline search consistency**
  - **Validates: Requirements 3.2**

- [x] 6. Implement get_music_impact() MCP tool




  - Register get_music_impact tool with FastMCP
  - Analyze timeline data to separate days with music (music_count > 0) vs without music (music_count = 0)
  - Calculate average commits for each group and percentage boost
  - Return JSON response with music_boost_percentage, days counts, and recommendation
  - Handle edge case when insufficient data for meaningful analysis
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7. Implement predict_commits(music_hours, video_minutes) MCP tool




  - Register predict_commits tool with FastMCP, accepting music_hours and video_minutes parameters
  - Implement parameter validation to ensure non-negative numeric values
  - Calculate prediction using simple linear model based on historical coefficients
  - Determine confidence level based on input similarity to historical patterns
  - Return JSON response with predicted_commits, confidence_level, factors_considered
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 7.1 Write property test for numeric parameter validation
  - **Property 7: Numeric parameter validation consistency**
  - **Validates: Requirements 5.1**

- [ ]* 7.2 Write property test for prediction calculations
  - **Property 8: Prediction calculation consistency**
  - **Validates: Requirements 5.2**

- [x] 8. Implement dashboard resource endpoint





  - Register flowstate://dashboard resource with FastMCP using @mcp.resource() decorator
  - Implement function to read FLOWSTATE_DASHBOARD_URL environment variable
  - Return S3 URL if configured, otherwise return localhost:5173 fallback
  - Provide resource metadata including description, content type, last modified
  - Handle resource unavailability with appropriate error messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 8.1 Write property test for resource registration
  - **Property 9: Resource registration consistency**
  - **Validates: Requirements 6.1**

- [ ]* 8.2 Write property test for URL fallback behavior
  - **Property 10: URL fallback consistency**
  - **Validates: Requirements 6.2, 6.3**

- [ ]* 8.3 Write property test for resource metadata
  - **Property 11: Resource metadata consistency**
  - **Validates: Requirements 6.4**

- [x] 9. Implement comprehensive error handling and logging




  - Add try-except blocks around all external operations (file I/O, JSON parsing)
  - Implement consistent error response format with descriptive messages
  - Add logging for server initialization, tool registration, and error conditions
  - Ensure no internal details are exposed in error messages to clients
  - Test error handling with missing files, corrupted JSON, invalid parameters
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 9.1 Write property test for exception handling
  - **Property 12: Exception handling consistency**
  - **Validates: Requirements 7.4**

- [ ]* 9.2 Write property test for server initialization logging
  - **Property 13: Server initialization consistency**
  - **Validates: Requirements 7.5**

- [x] 10. Implement server startup and tool registration



  - Create main execution block with if __name__ == "__main__"
  - Initialize FastMCP server with name "FlowState"
  - Register all five tools with proper decorators and type hints
  - Add server startup logging to show initialization status and available tools
  - Implement mcp.run(transport="stdio") for STDIO communication
  - _Requirements: 8.2, 8.3, 8.4, 8.5_

- [ ]* 10.1 Write property test for tool registration
  - **Property 14: Tool registration consistency**
  - **Validates: Requirements 8.3**

- [ ]* 10.2 Write property test for environment variable handling
  - **Property 15: Environment variable reading consistency**
  - **Validates: Requirements 8.4**

- [x] 11. Add type hints and input/output validation
  - Add comprehensive type hints for all function parameters and return values
  - Implement input parameter validation for all tools
  - Add output sanitization to prevent malformed JSON responses
  - Ensure consistent JSON response structures across all tools
  - Test with various input types and edge cases
  - _Requirements: 10.1, 10.2, 10.5_

- [ ]* 11.1 Write property test for input validation and output sanitization
  - **Property 16: Input validation and output sanitization consistency**
  - **Validates: Requirements 10.2**

- [ ]* 11.2 Write property test for error handling implementation
  - **Property 17: Error handling implementation consistency**
  - **Validates: Requirements 10.4**

- [ ]* 11.3 Write property test for response formatting
  - **Property 18: Response formatting consistency**
  - **Validates: Requirements 10.5**

- [x] 12. Update README.md with MCP server documentation
  - Add "MCP Server" section to existing README.md
  - Document installation of mcp[cli]>=0.9.0 dependency
  - Provide setup instructions for running the MCP server
  - Include examples of each tool call with parameters and expected responses
  - Show MCP client configuration example for integrating the server
  - Add troubleshooting section for common error scenarios
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 13. Integration testing and validation
  - Test complete MCP server startup and tool registration
  - Verify STDIO transport communication works correctly
  - Test each tool with real FlowState correlation data
  - Validate all tool responses match expected JSON schemas
  - Test error conditions: missing files, invalid parameters, corrupted data
  - Verify resource endpoint returns correct dashboard URL
  - Test server integration with sample MCP client configuration
  - _Requirements: All_

- [x] 14. Final verification and deployment preparation
  - Run complete FlowState pipeline to ensure correlations.json is current
  - Test MCP server with python scripts/mcp_server.py command
  - Verify all tools return sensible results with real productivity data
  - Test environment variable configuration for dashboard URL
  - Validate server can be added to MCP client configurations
  - Ensure all error messages are user-friendly and actionable
  - Document any limitations or known issues
  - _Requirements: All_