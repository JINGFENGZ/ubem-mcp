# UBEM Analysis MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> Urban Building Energy Model (UBEM) analysis tools for EnergyPlus simulations, packaged as a Model Context Protocol (MCP) server.

## 🌟 Features

- **Weather Analysis**: Identify hottest consecutive days sequence from EPW weather files
- **IDF Modification**: Automatically modify HVAC schedules for outage scenarios
- **Batch Simulation**: Run EnergyPlus simulations for multiple buildings efficiently
- **Data Extraction**: Extract zone temperatures and energy metrics from any output variable
- **Scenario Comparison**: Compare baseline vs modified HVAC scenarios
- **Fully Configurable**: All parameters exposed, minimal hardcoding
- **MCP Integration**: Standard MCP protocol for LLM integration

## 🎯 Design Philosophy

This MCP server is designed to be **maximally flexible and minimally opinionated**:

- ✅ **No hardcoded paths**: All directories and files specified by user
- ✅ **Configurable variables**: Extract any output variable, not just temperature
- ✅ **Auto-detection**: EnergyPlus installation auto-detected when possible
- ✅ **Optional parameters**: Sensible defaults, override anything
- ✅ **Universal applicability**: Works with any EnergyPlus project structure

## 📋 Installation

### Prerequisites

- Python 3.10 or higher
- EnergyPlus v25.1.0 (or compatible version)
- pip (Python package manager)

### Install from Source

```bash
git clone https://github.com/JINGFENGZ/ubem-mcp
cd ubem-mcp
pip install -e .
```

## ⚡ Quick Start

### 1. Set EnergyPlus Path (Optional)

The server auto-detects common EnergyPlus installation locations. If needed, set:

```bash
export ENERGYPLUS_ROOT="/path/to/EnergyPlus"
```

**Note**: No project-specific configuration required! All paths are passed as tool parameters.

### 2. Run the MCP Server

```bash
python -m ubem_analysis_mcp.server
```

### 3. Use with MCP Client

Configure your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "ubem-analysis": {
      "command": "python",
      "args": ["-m", "ubem_analysis_mcp.server"],
      "env": {
        "ENERGYPLUS_ROOT": "/path/to/EnergyPlus"
      }
    }
  }
}
```

**Or let it auto-detect:**

```json
{
  "mcpServers": {
    "ubem-analysis": {
      "command": "python",
      "args": ["-m", "ubem_analysis_mcp.server"]
    }
  }
}
```

## 🛠️ Tools

### 1. `analyze_weather_file`

Analyse EPW weather file to identify the hottest **consecutive N-day sequence** based on average daily temperature.

### 2. `modify_idf_hvac`

Modify single IDF file HVAC schedule to simulate blackout scenarios.

### 3. `batch_modify_idf_hvac`

Batch modify multiple IDF files to create modified scenario models.

### 4. `run_simulation`

Run EnergyPlus simulation for a single building.

### 5. `batch_simulate`

Run simulations for multiple buildings.

### 6. `analyze_results`

Analyse simulation results and calculate statistics.

### 7. `generate_hourly_temperatures`

Generate hourly temperature CSV from simulation results.

### 8. `create_temperature_comparison`

Create comparison CSV between baseline and modified scenarios.

## 📖 Usage Examples

### Complete Workflow: Extreme Heat & Outage Resilience Assessment

```python
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days
from ubem_analysis_mcp.tools.idf_modification import batch_modify_idf_hvac_schedule
from ubem_analysis_mcp.tools.simulation_tools import batch_simulate_buildings
from ubem_analysis_mcp.tools.data_analysis import create_comparison_csv

# Step 1: Find hottest consecutive 3-day sequence
weather_result = analyze_epw_hottest_days("weather/Shanghai.epw", top_n=3)
hottest_day = weather_result["earliest_hot_day"]  # First day of the sequence
start_month = hottest_day["month"]
start_day = hottest_day["day"]
print(f"HVAC outage will start from: {start_month:02d}/{start_day:02d} (Day 1 of heatwave)")

# Step 2: Create modified IDF files (simulate cooling outage)
modify_result = batch_modify_idf_hvac_schedule(
    idf_directory="baseline_models",
    output_directory="modified_models",
    idd_file="/path/to/Energy+.idd",
    schedule_action="disable_cooling",
    start_month=start_month,
    start_day=start_day
)
print(f"Modified {modify_result['successful_modifications']} IDF files")

# Step 3: Run baseline simulations
baseline_result = batch_simulate_buildings(
    idf_directory="baseline_models",
    weather_file="weather/Shanghai.epw",
    output_base_dir="results/baseline"
)

# Step 4: Run modified simulations
modified_result = batch_simulate_buildings(
    idf_directory="modified_models",
    weather_file="weather/Shanghai.epw",
    output_base_dir="results/modified"
)

# Step 5: Create comparison report
comparison_result = create_comparison_csv(
    baseline_results_dir="results/baseline",
    modified_results_dir="results/modified",
    output_csv="temperature_comparison.csv"
)
print(f"Mean temperature increase: {comparison_result['statistics']['mean_increase']:.2f}°C")
```

### Weather Analysis Only

```python
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days

result = analyze_epw_hottest_days("path/to/weather.epw", top_n=3)
if result["success"]:
    print(f"Hottest day: {result['earliest_hot_day']['date']}")
```

### IDF Modification Only

```python
from ubem_analysis_mcp.tools.idf_modification import modify_idf_hvac_schedule

# Disable cooling from July 15 onwards
result = modify_idf_hvac_schedule(
    idf_path="baseline_model.idf",
    output_path="modified_model.idf",
    idd_file="/path/to/Energy+.idd",
    schedule_action="disable_cooling",
    start_month=7,
    start_day=15
)
```

See [`examples/`](examples/) directory for more examples.

## ⚙️ Configuration

Default configuration uses environment variables:

- `UBEM_PROJECT_ROOT`: Your project root directory
- `ENERGYPLUS_ROOT`: EnergyPlus installation directory

Or edit `ubem_analysis_mcp/config.py` directly.

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/JINGFENGZ/ubem-mcp
cd ubem-mcp
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black ubem_analysis_mcp/
ruff check ubem_analysis_mcp/
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [FastMCP](https://github.com/jlowin/fastmcp) framework
- Uses [eppy](https://github.com/santoshphilip/eppy) for EnergyPlus IDF processing
- Inspired by [EnergyPlus-MCP](https://github.com/LBNL-ETA/EnergyPlus-MCP)

## 📬 Support

- **Issues**: https://github.com/JINGFENGZ/ubem-mcp/issues
- **Discussions**: https://github.com/JINGFENGZ/ubem-mcp/discussions

## 📊 Project Status

This project is actively maintained. Current version: **1.1.0**

---

Made with ❤️ by the UBEM Analysis Team

