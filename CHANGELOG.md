# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

