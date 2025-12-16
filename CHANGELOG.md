# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-16

### Added
- **IDF Modification Tools**: Programmatic IDF file modification for outage scenarios
  - `modify_idf_hvac`: Modify single IDF file HVAC schedules
  - `batch_modify_idf_hvac`: Batch modify multiple IDF files
- New `idf_modification.py` module with comprehensive HVAC schedule manipulation
- Support for multiple schedule actions:
  - `disable_cooling`: Disable cooling systems (for heatwave + outage scenarios)
  - `disable_heating`: Disable heating systems
  - `disable_all`: Disable all HVAC systems
  - `enable_all`: Restore normal operation
- Configurable outage periods with start/end dates
- Automatic EnergyPlus version upgrade in IDF files
- Automatic addition of zone temperature output variables
- Complete workflow example in `examples/idf_modification_example.py`

### Enhanced
- README with IDF modification examples and complete workflow
- Documentation with weather-driven IDF modification patterns
- Tool count increased from 6 to 8 tools
- Feature list updated to highlight IDF modification capabilities

### Technical
- `get_idd_file()` function in config module for IDD file auto-detection
- Schedule:Compact object creation for day-by-day HVAC control
- Batch processing with detailed success/failure reporting
- Full integration with existing MCP server architecture

## [1.0.0] - 2025-11-26

### Added
- Initial release of UBEM Analysis MCP Server
- Weather analysis tools for EPW files
- Single and batch EnergyPlus simulation support
- Temperature data extraction and analysis
- Baseline vs modified scenario comparison
- Hourly temperature CSV generation
- MCP protocol integration with FastMCP
- Complete documentation
- Example usage scripts
- MIT License

### Features
- `analyze_weather_file`: Identify hottest days from EPW weather data
- `run_simulation`: Run single building EnergyPlus simulation
- `batch_simulate`: Batch process multiple buildings
- `analyze_results`: Calculate temperature statistics
- `generate_hourly_temperatures`: Extract hourly temperature data
- `create_temperature_comparison`: Generate baseline vs modified comparison CSV

### Technical
- Python 3.10+ support
- Async MCP server implementation
- Modular tool architecture
- Comprehensive error handling
- JSON output format for all tools
- Environment variable configuration support

---

[1.0.0]: https://github.com/JINGFENGZ/ubem-mcp/releases/tag/v1.0.0


