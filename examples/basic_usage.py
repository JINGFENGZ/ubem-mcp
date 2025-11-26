"""
Basic usage examples for UBEM Analysis MCP Server

This example demonstrates common workflows.
Update paths according to your local setup.
"""

from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days
from ubem_analysis_mcp.tools.simulation_tools import run_energyplus_simulation
from ubem_analysis_mcp.config import get_config


def example_weather_analysis():
    """Example 1: Analyze weather file"""
    print("="*80)
    print("Example 1: Weather Analysis")
    print("="*80)
    
    # Update with your weather file path
    epw_file = "path/to/your/weather.epw"
    
    result = analyze_epw_hottest_days(epw_file, top_n=3)
    
    if result["success"]:
        print(f"\nHottest days in {result['epw_file']}:")
        for day in result["top_hottest_days"]:
            print(f"  {day['date']}: Avg {day['average_temperature']}°C, "
                  f"Max {day['maximum_temperature']}°C")
        
        print(f"\nEarliest hot day: {result['earliest_hot_day']['date']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


def example_single_simulation():
    """Example 2: Run a single simulation"""
    print("\n" + "="*80)
    print("Example 2: Single Building Simulation")
    print("="*80)
    
    config = get_config()
    
    # Update with your IDF file path
    idf_path = "path/to/your/building.idf"
    weather_file = "path/to/your/weather.epw"
    output_dir = "simulation_output"
    
    result = run_energyplus_simulation(
        idf_path,
        weather_file,
        output_dir,
        config["energyplus_exe"],
        config["expand_objects_exe"]
    )
    
    if result["success"]:
        print(f"\n✓ Simulation successful!")
        print(f"  Output: {result['output_directory']}")
    else:
        print(f"\n✗ Simulation failed!")
        print(f"  Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    print("\nUBEM Analysis MCP Server - Basic Usage Examples\n")
    print("NOTE: Update file paths in this script before running!\n")
    
    # Uncomment to run examples
    # example_weather_analysis()
    # example_single_simulation()
    
    print("Update paths in basic_usage.py and uncomment examples to run.")

