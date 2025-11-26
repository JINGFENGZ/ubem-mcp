"""
UBEM Analysis MCP Server
Urban Building Energy Model Analysis Tools for EnergyPlus Simulations
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

# Import tools
from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days
from ubem_analysis_mcp.tools.simulation_tools import (
    run_energyplus_simulation,
    batch_simulate_buildings
)
from ubem_analysis_mcp.tools.data_analysis import (
    analyze_simulation_results,
    generate_hourly_csv,
    create_comparison_csv
)
from ubem_analysis_mcp.config import get_config

# Initialize FastMCP server
mcp = FastMCP(name="ubem_analysis")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_config()

logger.info("UBEM Analysis MCP Server initialized")


@mcp.prompt(name="ubem_analysis_instructions")
def ubem_analysis_instructions():
    """Instructions for using the UBEM Analysis MCP Server"""
    return """
# UBEM Analysis MCP Server Instructions

This MCP server provides Urban Building Energy Model (UBEM) analysis tools for EnergyPlus simulations.

## Available Tools:

### 1. Weather Analysis
- **analyze_weather_file**: Identify hottest days from EPW weather data

### 2. Simulation Tools  
- **run_simulation**: Run EnergyPlus simulation for a single building
- **batch_simulate**: Run simulations for multiple buildings

### 3. Data Analysis
- **analyze_results**: Analyze and compare simulation results
- **generate_hourly_temperatures**: Extract hourly temperature data
- **create_temperature_comparison**: Create baseline vs modified comparison

## Typical Workflow:

1. **Analyze Weather**: Identify hottest days from EPW file
2. **Modify IDF**: Create modified building models
3. **Run Simulations**: Execute baseline and modified scenarios
4. **Analyze Results**: Extract and compare temperature data
5. **Generate Reports**: Create CSV files for analysis

## Configuration:

Update paths in config.py or set environment variables:
- UBEM_PROJECT_ROOT: Your project root directory
- ENERGYPLUS_ROOT: EnergyPlus installation directory

See documentation for more details.
"""


@mcp.tool()
def analyze_weather_file(
    epw_file_path: str,
    top_n: int = 3
) -> str:
    """
    Analyze EPW weather file to identify the hottest days.
    
    Identifies days with highest average dry bulb temperature and finds
    the earliest day among the hottest days.
    
    Args:
        epw_file_path: Path to EPW file
        top_n: Number of hottest days to identify (default: 3)
    
    Returns:
        JSON string containing hottest days analysis
    """
    logger.info(f"Analyzing weather file: {epw_file_path}")
    
    try:
        result = analyze_epw_hottest_days(epw_file_path, top_n)
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error analyzing weather file: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "epw_file": epw_file_path
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def run_simulation(
    idf_path: str,
    weather_file: Optional[str] = None,
    output_dir: str = "simulation_output",
    use_expand_objects: bool = True
) -> str:
    """
    Run EnergyPlus simulation for a single IDF file.
    
    Args:
        idf_path: Path to IDF file
        weather_file: Path to weather file (default: uses config)
        output_dir: Output directory for results
        use_expand_objects: Whether to run ExpandObjects (default: True)
    
    Returns:
        JSON string containing simulation status
    """
    logger.info(f"Running simulation: {idf_path}")
    
    try:
        if not weather_file:
            weather_file = config["weather_file"]
        
        expand_objects_exe = config["expand_objects_exe"] if use_expand_objects else None
        
        result = run_energyplus_simulation(
            idf_path,
            weather_file,
            output_dir,
            config["energyplus_exe"],
            expand_objects_exe
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "idf_file": idf_path
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def batch_simulate(
    idf_directory: str,
    output_base_dir: str,
    weather_file: Optional[str] = None,
    use_expand_objects: bool = True,
    max_buildings: Optional[int] = None
) -> str:
    """
    Run EnergyPlus simulations for multiple buildings.
    
    Args:
        idf_directory: Directory containing IDF files
        output_base_dir: Base directory for all outputs
        weather_file: Path to weather file (default: uses config)
        use_expand_objects: Whether to run ExpandObjects (default: True)
        max_buildings: Maximum number of buildings to simulate (optional)
    
    Returns:
        JSON string containing batch simulation status
    """
    logger.info(f"Batch simulating buildings from: {idf_directory}")
    
    try:
        if not weather_file:
            weather_file = config["weather_file"]
        
        expand_objects_exe = config["expand_objects_exe"] if use_expand_objects else None
        
        result = batch_simulate_buildings(
            idf_directory,
            weather_file,
            output_base_dir,
            config["energyplus_exe"],
            expand_objects_exe,
            max_buildings
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in batch simulation: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def analyze_results(
    baseline_results_dir: str,
    modified_results_dir: Optional[str] = None
) -> str:
    """
    Analyze simulation results and calculate temperature statistics.
    
    Args:
        baseline_results_dir: Directory containing baseline simulation results
        modified_results_dir: Directory containing modified results (optional)
    
    Returns:
        JSON string containing analysis results
    """
    logger.info(f"Analyzing results from: {baseline_results_dir}")
    
    try:
        result = analyze_simulation_results(
            baseline_results_dir,
            modified_results_dir
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error analyzing results: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def generate_hourly_temperatures(
    results_dir: str,
    output_csv: str
) -> str:
    """
    Generate hourly temperature CSV from simulation results.
    
    Creates a CSV file with hourly temperatures for all buildings.
    Each row represents an hour (8760 total), each column a building.
    
    Args:
        results_dir: Directory containing simulation results
        output_csv: Output CSV file path
    
    Returns:
        JSON string containing generation status
    """
    logger.info(f"Generating hourly temperatures CSV: {output_csv}")
    
    try:
        result = generate_hourly_csv(results_dir, output_csv)
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating hourly CSV: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "output_file": output_csv
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def create_temperature_comparison(
    baseline_results_dir: str,
    modified_results_dir: str,
    output_csv: str
) -> str:
    """
    Create comparison CSV between baseline and modified scenarios.
    
    Generates a CSV file comparing annual average temperatures between
    baseline and modified scenarios for all buildings.
    
    Args:
        baseline_results_dir: Directory containing baseline results
        modified_results_dir: Directory containing modified results
        output_csv: Output CSV file path
    
    Returns:
        JSON string containing creation status
    """
    logger.info(f"Creating temperature comparison CSV: {output_csv}")
    
    try:
        result = create_comparison_csv(
            baseline_results_dir,
            modified_results_dir,
            output_csv
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating comparison CSV: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "output_file": output_csv
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio")

