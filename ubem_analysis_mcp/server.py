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
    weather_file: str,
    output_dir: str = "simulation_output",
    energyplus_exe: Optional[str] = None,
    expand_objects_exe: Optional[str] = None,
    timeout: int = 600
) -> str:
    """
    Run EnergyPlus simulation for a single IDF file.
    
    Args:
        idf_path: Path to IDF file
        weather_file: Path to weather file
        output_dir: Output directory for results (default: 'simulation_output')
        energyplus_exe: Path to EnergyPlus executable (default: auto-detect)
        expand_objects_exe: Path to ExpandObjects executable (default: auto-detect, None to skip)
        timeout: Simulation timeout in seconds (default: 600)
    
    Returns:
        JSON string containing simulation status
    """
    logger.info(f"Running simulation: {idf_path}")
    
    try:
        # Auto-detect EnergyPlus executable if not provided
        if not energyplus_exe:
            from ubem_analysis_mcp.config import get_energyplus_executable
            energyplus_exe = get_energyplus_executable()
            if not energyplus_exe:
                raise FileNotFoundError(
                    "EnergyPlus executable not found. Please provide energyplus_exe parameter "
                    "or set ENERGYPLUS_ROOT environment variable."
                )
        
        # Auto-detect ExpandObjects if not explicitly disabled
        if expand_objects_exe is None:
            from ubem_analysis_mcp.config import get_expand_objects_executable
            expand_objects_exe = get_expand_objects_executable()
        
        result = run_energyplus_simulation(
            idf_path,
            weather_file,
            output_dir,
            energyplus_exe,
            expand_objects_exe,
            timeout
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
    weather_file: str,
    output_base_dir: str,
    energyplus_exe: Optional[str] = None,
    expand_objects_exe: Optional[str] = None,
    max_buildings: Optional[int] = None,
    timeout: int = 600
) -> str:
    """
    Run EnergyPlus simulations for multiple buildings.
    
    Args:
        idf_directory: Directory containing IDF files
        weather_file: Path to weather file
        output_base_dir: Base directory for all outputs
        energyplus_exe: Path to EnergyPlus executable (default: auto-detect)
        expand_objects_exe: Path to ExpandObjects executable (default: auto-detect, None to skip)
        max_buildings: Maximum number of buildings to simulate (optional)
        timeout: Simulation timeout per building in seconds (default: 600)
    
    Returns:
        JSON string containing batch simulation status
    """
    logger.info(f"Batch simulating buildings from: {idf_directory}")
    
    try:
        # Auto-detect EnergyPlus executable if not provided
        if not energyplus_exe:
            from ubem_analysis_mcp.config import get_energyplus_executable
            energyplus_exe = get_energyplus_executable()
            if not energyplus_exe:
                raise FileNotFoundError(
                    "EnergyPlus executable not found. Please provide energyplus_exe parameter "
                    "or set ENERGYPLUS_ROOT environment variable."
                )
        
        # Auto-detect ExpandObjects if not explicitly disabled
        if expand_objects_exe is None:
            from ubem_analysis_mcp.config import get_expand_objects_executable
            expand_objects_exe = get_expand_objects_executable()
        
        result = batch_simulate_buildings(
            idf_directory,
            weather_file,
            output_base_dir,
            energyplus_exe,
            expand_objects_exe,
            max_buildings,
            timeout
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
    modified_results_dir: Optional[str] = None,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    temperature_unit: str = 'C'
) -> str:
    """
    Analyze simulation results and calculate temperature statistics.
    
    Args:
        baseline_results_dir: Directory containing baseline simulation results
        modified_results_dir: Directory containing modified results (optional)
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns 
                                   (default: 'Zone Mean Air Temperature')
        temperature_unit: Temperature unit for display (default: 'C')
    
    Returns:
        JSON string containing analysis results
    """
    logger.info(f"Analyzing results from: {baseline_results_dir}")
    
    try:
        result = analyze_simulation_results(
            baseline_results_dir,
            modified_results_dir,
            output_csv_name,
            temperature_column_pattern,
            temperature_unit
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
    output_csv: str,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    time_column_name: str = 'Hour'
) -> str:
    """
    Generate hourly temperature CSV from simulation results.
    
    Creates a CSV file with hourly temperatures for all buildings.
    Each row represents an hour (typically 8760), each column a building.
    
    Args:
        results_dir: Directory containing simulation results
        output_csv: Output CSV file path
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns 
                                   (default: 'Zone Mean Air Temperature')
        time_column_name: Name of the time column in output (default: 'Hour')
    
    Returns:
        JSON string containing generation status
    """
    logger.info(f"Generating hourly temperatures CSV: {output_csv}")
    
    try:
        result = generate_hourly_csv(
            results_dir, 
            output_csv,
            output_csv_name,
            temperature_column_pattern,
            time_column_name
        )
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
    output_csv: str,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    temperature_unit: str = 'C'
) -> str:
    """
    Create comparison CSV between baseline and modified scenarios.
    
    Generates a CSV file comparing annual average temperatures between
    baseline and modified scenarios for all buildings.
    
    Args:
        baseline_results_dir: Directory containing baseline results
        modified_results_dir: Directory containing modified results
        output_csv: Output CSV file path
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns 
                                   (default: 'Zone Mean Air Temperature')
        temperature_unit: Temperature unit for display (default: 'C')
    
    Returns:
        JSON string containing creation status
    """
    logger.info(f"Creating temperature comparison CSV: {output_csv}")
    
    try:
        result = create_comparison_csv(
            baseline_results_dir,
            modified_results_dir,
            output_csv,
            output_csv_name,
            temperature_column_pattern,
            temperature_unit
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

