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
from ubem_analysis_mcp.tools.idf_modification import (
    modify_idf_hvac_schedule,
    batch_modify_idf_hvac_schedule
)
from ubem_analysis_mcp.tools.thermal_comfort_analysis import (
    load_hourly_temperature_data,
    analyse_comfort_thresholds,
    generate_comfort_visualisations,
    generate_comfort_report
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

### 2. IDF Modification
- **modify_idf_hvac**: Modify single IDF file HVAC schedule
- **batch_modify_idf_hvac**: Batch modify multiple IDF files

### 3. Simulation Tools  
- **run_simulation**: Run EnergyPlus simulation for a single building
- **batch_simulate**: Run simulations for multiple buildings

### 4. Data Analysis
- **analyze_results**: Analyse and compare simulation results
- **generate_hourly_temperatures**: Extract hourly temperature data
- **create_temperature_comparison**: Create baseline vs modified comparison

## Typical Workflow:

1. **Analyse Weather**: Identify hottest days from EPW file
2. **Modify IDF Files**: Automatically modify HVAC schedules for outage scenarios
3. **Run Simulations**: Execute baseline and modified scenarios
4. **Analyse Results**: Extract and compare temperature data
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
    Analyse EPW weather file to identify the hottest days.
    
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
    Analyse simulation results and calculate temperature statistics.
    
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


@mcp.tool()
def modify_idf_hvac(
    idf_path: str,
    output_path: str,
    schedule_action: str = "disable_cooling",
    start_month: int = 7,
    start_day: int = 15,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    schedule_name: Optional[str] = None,
    idd_file: Optional[str] = None,
    target_version: str = "25.1.0"
) -> str:
    """
    Modify IDF file HVAC schedule to simulate blackout or outage scenarios.
    
    Creates or modifies a schedule that controls HVAC system availability,
    useful for simulating power outages during extreme weather events.
    
    Args:
        idf_path: Path to the source IDF file
        output_path: Path where the modified IDF will be saved
        schedule_action: Type of HVAC modification:
            - "disable_cooling": Disable cooling systems (default)
            - "disable_heating": Disable heating systems
            - "disable_all": Disable all HVAC systems
            - "enable_all": Enable all HVAC systems
        start_month: Month when the schedule change begins (1-12, default: 7)
        start_day: Day when the schedule change begins (1-31, default: 15)
        end_month: Month when the schedule change ends (optional, None means until end of year)
        end_day: Day when the schedule change ends (optional)
        schedule_name: Custom name for the created schedule (optional)
        idd_file: Path to Energy+.idd file (default: auto-detect)
        target_version: EnergyPlus version to set in the IDF file (default: 25.1.0)
    
    Returns:
        JSON string containing modification status and details
    """
    logger.info(f"Modifying IDF file: {idf_path}")
    
    try:
        # Auto-detect IDD file if not provided
        if not idd_file:
            from ubem_analysis_mcp.config import get_idd_file
            idd_file = get_idd_file()
            if not idd_file:
                raise FileNotFoundError(
                    "IDD file not found. Please provide idd_file parameter "
                    "or set ENERGYPLUS_ROOT environment variable."
                )
        
        result = modify_idf_hvac_schedule(
            idf_path=idf_path,
            output_path=output_path,
            idd_file=idd_file,
            schedule_action=schedule_action,
            start_month=start_month,
            start_day=start_day,
            end_month=end_month,
            end_day=end_day,
            schedule_name=schedule_name,
            target_version=target_version
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error modifying IDF: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "idf_file": idf_path,
            "output_file": output_path
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def batch_modify_idf_hvac(
    idf_directory: str,
    output_directory: str,
    schedule_action: str = "disable_cooling",
    start_month: int = 7,
    start_day: int = 15,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    schedule_name: Optional[str] = None,
    idd_file: Optional[str] = None,
    target_version: str = "25.1.0",
    max_buildings: Optional[int] = None
) -> str:
    """
    Batch modify multiple IDF files to simulate blackout scenarios.
    
    Processes all IDF files in a directory and applies HVAC schedule
    modifications to simulate power outages during extreme weather events.
    
    Args:
        idf_directory: Directory containing IDF files to modify
        output_directory: Directory where modified IDF files will be saved
        schedule_action: Type of HVAC modification (see modify_idf_hvac)
        start_month: Month when the schedule change begins (1-12, default: 7)
        start_day: Day when the schedule change begins (1-31, default: 15)
        end_month: Month when the schedule change ends (optional)
        end_day: Day when the schedule change ends (optional)
        schedule_name: Custom name for the created schedule (optional)
        idd_file: Path to Energy+.idd file (default: auto-detect)
        target_version: EnergyPlus version to set in the IDF files (default: 25.1.0)
        max_buildings: Maximum number of buildings to process (optional, for testing)
    
    Returns:
        JSON string containing batch modification status
    """
    logger.info(f"Batch modifying IDF files from: {idf_directory}")
    
    try:
        # Auto-detect IDD file if not provided
        if not idd_file:
            from ubem_analysis_mcp.config import get_idd_file
            idd_file = get_idd_file()
            if not idd_file:
                raise FileNotFoundError(
                    "IDD file not found. Please provide idd_file parameter "
                    "or set ENERGYPLUS_ROOT environment variable."
                )
        
        result = batch_modify_idf_hvac_schedule(
            idf_directory=idf_directory,
            output_directory=output_directory,
            idd_file=idd_file,
            schedule_action=schedule_action,
            start_month=start_month,
            start_day=start_day,
            end_month=end_month,
            end_day=end_day,
            schedule_name=schedule_name,
            target_version=target_version,
            max_buildings=max_buildings
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in batch IDF modification: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


@mcp.tool()
def analyse_thermal_comfort(
    baseline_csv: str,
    modified_csv: str,
    output_dir: str,
    event_start_hour: int,
    event_name: str = "Event",
    building_type_map: Optional[str] = None,
    comfort_thresholds: Optional[str] = None,
    generate_visualisations: bool = True
) -> str:
    """
    Analyse thermal comfort impact by comparing baseline and modified scenarios.
    
    Compares hourly zone temperature data between baseline and modified scenarios,
    analyses comfort threshold breaches, and generates visualisation charts.
    
    Args:
        baseline_csv: Path to baseline hourly temperature CSV file
        modified_csv: Path to modified hourly temperature CSV file
        output_dir: Directory for output files (figures and reports)
        event_start_hour: Hour when the event starts (e.g., 4681 for July 15)
        event_name: Name of the event (e.g., "Heatwave", "Power Outage")
        building_type_map: Optional JSON string of building type mapping
                          e.g., '{"0": "Lowrise_Domestic", "1": "Midrise_Domestic", ...}'
        comfort_thresholds: Optional JSON string of comfort thresholds in °C
                           e.g., '{"comfort_limit": 26, "acceptable_limit": 28, ...}'
        generate_visualisations: Whether to generate visualisation charts (default: True)
    
    Returns:
        JSON string with analysis results including statistics and file paths
    
    Example:
        analyse_thermal_comfort(
            baseline_csv="baseline_temps.csv",
            modified_csv="modified_temps.csv",
            output_dir="./comfort_analysis",
            event_start_hour=4681,
            event_name="Heatwave",
            generate_visualisations=True
        )
    """
    try:
        logger.info(f"Analysing thermal comfort: {baseline_csv} vs {modified_csv}")
        
        # Parse optional parameters
        bldg_type_map = None
        if building_type_map:
            bldg_type_map = json.loads(building_type_map)
        
        thresholds = None
        if comfort_thresholds:
            thresholds = json.loads(comfort_thresholds)
        
        # Load data
        baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
            baseline_file=baseline_csv,
            modified_file=modified_csv,
            building_type_map=bldg_type_map
        )
        
        logger.info(f"Loaded data: {len(baseline_df)} hours, {len(building_cols)} buildings")
        
        # Analyse comfort thresholds
        threshold_results = analyse_comfort_thresholds(
            baseline_df=baseline_df,
            modified_df=modified_df,
            building_cols=building_cols,
            start_hour=event_start_hour,
            thresholds=thresholds
        )
        
        logger.info("Comfort threshold analysis complete")
        
        # Generate visualisations if requested
        vis_files = {}
        if generate_visualisations:
            vis_files = generate_comfort_visualisations(
                baseline_df=baseline_df,
                modified_df=modified_df,
                building_cols=building_cols,
                building_labels=building_labels,
                start_hour=event_start_hour,
                output_dir=output_dir,
                event_name=event_name
            )
            logger.info(f"Generated {len(vis_files)} visualisation files")
        
        # Generate report
        report_file = str(Path(output_dir) / f'thermal_comfort_report_{event_name.lower().replace(" ", "_")}.txt')
        summary = generate_comfort_report(
            baseline_df=baseline_df,
            modified_df=modified_df,
            building_cols=building_cols,
            start_hour=event_start_hour,
            threshold_results=threshold_results,
            output_file=report_file,
            event_name=event_name
        )
        
        logger.info(f"Report generated: {report_file}")
        
        # Combine results
        result = {
            "success": True,
            "num_buildings": len(building_cols),
            "event_start_hour": event_start_hour,
            "event_name": event_name,
            "summary": summary,
            "visualisation_files": vis_files,
            "output_directory": output_dir
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in thermal comfort analysis: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="stdio")

