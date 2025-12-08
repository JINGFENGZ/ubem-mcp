# UBEM Analysis MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> Urban Building Energy Model (UBEM) analysis tools for EnergyPlus simulations, packaged as a Model Context Protocol (MCP) server.

## 🌟 Features

- **Weather Analysis**: Identify hottest days from EPW weather files
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

Analyze EPW weather file to identify the hottest days.

### 2. `run_simulation`

Run EnergyPlus simulation for a single building.

### 3. `batch_simulate`

Run simulations for multiple buildings.

### 4. `analyze_results`

Analyze simulation results and calculate statistics.

### 5. `generate_hourly_temperatures`

Generate hourly temperature CSV from simulation results.

### 6. `create_temperature_comparison`

Create comparison CSV between baseline and modified scenarios.

## 📖 Usage Examples

### Weather Analysis

```python
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days

result = analyze_epw_hottest_days("path/to/weather.epw", top_n=3)
if result["success"]:
    print(f"Hottest day: {result['earliest_hot_day']['date']}")
```

### Batch Simulations

```python
from ubem_analysis_mcp.tools.simulation_tools import batch_simulate_buildings

result = batch_simulate_buildings(
    idf_directory="baseline_models",
    weather_file="weather.epw",
    output_base_dir="simulation_results",
    energyplus_exe="/path/to/energyplus",
    max_buildings=10  # Optional: limit for testing
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

This project is actively maintained. Current version: **1.0.0**

---

Made with ❤️ by the UBEM Analysis Team

