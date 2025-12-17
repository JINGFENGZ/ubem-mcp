"""
Example: IDF Modification for Outage Scenarios

This example demonstrates how to modify IDF files to simulate
HVAC system outages during extreme weather events.
"""

from ubem_analysis_mcp.tools.weather_analysis import analyze_epw_hottest_days
from ubem_analysis_mcp.tools.idf_modification import (
    modify_idf_hvac_schedule,
    batch_modify_idf_hvac_schedule
)
from ubem_analysis_mcp.config import get_idd_file


def example_single_idf_modification():
    """Modify a single IDF file to disable cooling from July 15."""
    
    print("="*80)
    print("Example 1: Single IDF Modification")
    print("="*80)
    
    # Get IDD file path (auto-detect or specify)
    idd_file = get_idd_file()
    if not idd_file:
        print("Error: IDD file not found. Set ENERGYPLUS_ROOT environment variable.")
        return
    
    result = modify_idf_hvac_schedule(
        idf_path="path/to/baseline_building.idf",
        output_path="path/to/modified_building.idf",
        idd_file=idd_file,
        schedule_action="disable_cooling",
        start_month=7,
        start_day=15
    )
    
    if result["success"]:
        print(f"✓ Success!")
        print(f"  Output: {result['output_file']}")
        print(f"  Schedule: {result['schedule_name']}")
        print(f"  Action: {result['schedule_action']}")
        print(f"  Period: {result['start_date']} to {result['end_date']}")
        print(f"  Systems modified: {result['systems_modified']}")
    else:
        print(f"✗ Failed: {result['error']}")


def example_batch_idf_modification():
    """Batch modify all IDF files in a directory."""
    
    print("\n" + "="*80)
    print("Example 2: Batch IDF Modification")
    print("="*80)
    
    idd_file = get_idd_file()
    if not idd_file:
        print("Error: IDD file not found. Set ENERGYPLUS_ROOT environment variable.")
        return
    
    result = batch_modify_idf_hvac_schedule(
        idf_directory="baseline_models",
        output_directory="modified_models_cooling_disabled",
        idd_file=idd_file,
        schedule_action="disable_cooling",
        start_month=7,
        start_day=15
    )
    
    if result["success"]:
        print(f"✓ Batch modification complete!")
        print(f"  Total buildings: {result['total_buildings']}")
        print(f"  Successful: {result['successful_modifications']}")
        print(f"  Failed: {result['failed_modifications']}")
        print(f"  Success rate: {result['success_rate']}")
    else:
        print(f"✗ Batch modification failed: {result['error']}")


def example_weather_driven_modification():
    """Use weather analysis to determine when to disable HVAC."""
    
    print("\n" + "="*80)
    print("Example 3: Weather-Driven IDF Modification")
    print("="*80)
    
    # Step 1: Analyse weather to find hottest days
    print("\nStep 1: Analysing weather file...")
    weather_result = analyze_epw_hottest_days(
        epw_file="weather/Shanghai.epw",
        top_n=3
    )
    
    if not weather_result["success"]:
        print(f"✗ Weather analysis failed: {weather_result['error']}")
        return
    
    # Extract earliest hot day
    earliest_hot_day = weather_result["earliest_hot_day"]
    start_month = earliest_hot_day["month"]
    start_day = earliest_hot_day["day"]
    
    print(f"✓ Hottest period starts from: {start_month:02d}/{start_day:02d}")
    print(f"  Top 3 hottest days:")
    for hot_day in weather_result["top_hottest_days"]:
        print(f"    - {hot_day['date']}: {hot_day['average_temperature']:.1f}°C")
    
    # Step 2: Modify IDF files based on weather analysis
    print(f"\nStep 2: Modifying IDF files (cooling disabled from {start_month:02d}/{start_day:02d})...")
    
    idd_file = get_idd_file()
    if not idd_file:
        print("Error: IDD file not found.")
        return
    
    modify_result = batch_modify_idf_hvac_schedule(
        idf_directory="baseline_models",
        output_directory="modified_models_weather_driven",
        idd_file=idd_file,
        schedule_action="disable_cooling",
        start_month=start_month,
        start_day=start_day,
        max_buildings=10  # Limit to 10 for testing
    )
    
    if modify_result["success"]:
        print(f"✓ Modified {modify_result['successful_modifications']} IDF files")
    else:
        print(f"✗ Failed: {modify_result['error']}")


def example_different_scenarios():
    """Create multiple scenario variants with different HVAC actions."""
    
    print("\n" + "="*80)
    print("Example 4: Multiple Scenario Creation")
    print("="*80)
    
    idd_file = get_idd_file()
    if not idd_file:
        print("Error: IDD file not found.")
        return
    
    scenarios = [
        {
            "name": "Scenario 1: Cooling Disabled (Full Summer)",
            "action": "disable_cooling",
            "start": (6, 1),  # June 1
            "end": (9, 30),   # September 30
            "output_dir": "scenarios/no_cooling_summer"
        },
        {
            "name": "Scenario 2: Cooling Disabled (Hottest Month)",
            "action": "disable_cooling",
            "start": (7, 15),  # July 15
            "end": (8, 15),    # August 15
            "output_dir": "scenarios/no_cooling_july_aug"
        },
        {
            "name": "Scenario 3: All HVAC Disabled (Emergency)",
            "action": "disable_all",
            "start": (7, 20),  # July 20
            "end": (7, 25),    # July 25
            "output_dir": "scenarios/complete_outage"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"  Period: {scenario['start'][0]:02d}/{scenario['start'][1]:02d} to "
              f"{scenario['end'][0]:02d}/{scenario['end'][1]:02d}")
        
        result = batch_modify_idf_hvac_schedule(
            idf_directory="baseline_models",
            output_directory=scenario["output_dir"],
            idd_file=idd_file,
            schedule_action=scenario["action"],
            start_month=scenario["start"][0],
            start_day=scenario["start"][1],
            end_month=scenario["end"][0],
            end_day=scenario["end"][1],
            max_buildings=5  # Test with 5 buildings
        )
        
        if result["success"]:
            print(f"  ✓ Created: {result['successful_modifications']} files")
        else:
            print(f"  ✗ Failed: {result['error']}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("IDF Modification Examples")
    print("="*80)
    print("\nThese examples demonstrate how to modify IDF files to simulate")
    print("HVAC outages during extreme weather events.")
    print("\nNote: Update file paths to match your project structure before running.")
    print("="*80)
    
    # Run examples (uncomment to execute)
    # example_single_idf_modification()
    # example_batch_idf_modification()
    # example_weather_driven_modification()
    # example_different_scenarios()
    
    print("\n✓ Example script loaded successfully.")
    print("  Uncomment function calls in __main__ to run examples.")


