"""
Example: Thermal Comfort Analysis

This example demonstrates how to use the thermal comfort analysis tool
to compare baseline and modified scenarios.
"""

from ubem_analysis_mcp.tools.thermal_comfort_analysis import (
    load_hourly_temperature_data,
    analyse_comfort_thresholds,
    generate_comfort_visualisations,
    generate_comfort_report
)

# Example 1: Basic thermal comfort analysis
def example_basic_analysis():
    """Basic thermal comfort analysis with default settings"""
    
    # Load hourly temperature data
    baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
        baseline_file="hourly_zone_temperatures_baseline.csv",
        modified_file="hourly_zone_temperatures_modified.csv"
    )
    
    # Analyse comfort thresholds
    # Event starts at hour 4681 (July 15, 00:00)
    threshold_results = analyse_comfort_thresholds(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        start_hour=4681
    )
    
    print("Threshold Breach Analysis:")
    for threshold_name, results in threshold_results.items():
        print(f"\n{threshold_name}:")
        print(f"  Threshold: {results['threshold_temp']}°C")
        print(f"  Modified breach ratio: {results['modified_breach_ratio']:.2f}%")
        print(f"  Increase: {results['increase']:.2f} percentage points")
        if results['first_breach_time']:
            print(f"  First breach: {results['first_breach_time']}")


# Example 2: Generate visualisations
def example_generate_visualisations():
    """Generate thermal comfort visualisation charts"""
    
    # Load data
    baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
        baseline_file="hourly_zone_temperatures_baseline.csv",
        modified_file="hourly_zone_temperatures_modified.csv"
    )
    
    # Generate visualisations
    vis_files = generate_comfort_visualisations(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        building_labels=building_labels,
        start_hour=4681,
        output_dir="./comfort_analysis_output",
        event_name="Heatwave"
    )
    
    print("Generated visualisations:")
    for vis_type, file_path in vis_files.items():
        print(f"  {vis_type}: {file_path}")


# Example 3: Custom building type mapping
def example_custom_building_types():
    """Use custom building type mapping"""
    
    # Define custom building type mapping
    custom_mapping = {
        '0': 'Residential_Low',
        '1': 'Residential_Mid',
        '2': 'Residential_High',
        '3': 'Retail',
        '4': 'Business',
        '5': 'Factory',
        '6': 'Station',
        '7': 'Government'
    }
    
    # Load data with custom mapping
    baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
        baseline_file="hourly_zone_temperatures_baseline.csv",
        modified_file="hourly_zone_temperatures_modified.csv",
        building_type_map=custom_mapping
    )
    
    print(f"Loaded {len(building_cols)} buildings with custom labels")
    print("Sample labels:", list(building_labels.values())[:5])


# Example 4: Custom comfort thresholds
def example_custom_thresholds():
    """Use custom comfort thresholds"""
    
    # Load data
    baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
        baseline_file="hourly_zone_temperatures_baseline.csv",
        modified_file="hourly_zone_temperatures_modified.csv"
    )
    
    # Define custom thresholds (e.g., for different climate zones)
    custom_thresholds = {
        'comfort_limit': 28,      # Higher comfort limit for hot climates
        'acceptable_limit': 30,   # Adjusted acceptable limit
        'health_risk': 32,        # Health risk threshold
        'severe_risk': 37         # Severe risk threshold
    }
    
    # Analyse with custom thresholds
    threshold_results = analyse_comfort_thresholds(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        start_hour=4681,
        thresholds=custom_thresholds
    )
    
    print("Custom threshold analysis complete")


# Example 5: Complete workflow
def example_complete_workflow():
    """Complete thermal comfort analysis workflow"""
    
    # Configuration
    baseline_csv = "hourly_zone_temperatures_baseline.csv"
    modified_csv = "hourly_zone_temperatures_modified.csv"
    output_dir = "./comfort_analysis"
    event_start_hour = 4681  # July 15
    event_name = "Cooling System Outage"
    
    # Step 1: Load data
    print("Step 1: Loading data...")
    baseline_df, modified_df, building_cols, building_labels = load_hourly_temperature_data(
        baseline_file=baseline_csv,
        modified_file=modified_csv
    )
    print(f"  Loaded {len(baseline_df)} hours, {len(building_cols)} buildings")
    
    # Step 2: Analyse thresholds
    print("\nStep 2: Analysing comfort thresholds...")
    threshold_results = analyse_comfort_thresholds(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        start_hour=event_start_hour
    )
    print("  Threshold analysis complete")
    
    # Step 3: Generate visualisations
    print("\nStep 3: Generating visualisations...")
    vis_files = generate_comfort_visualisations(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        building_labels=building_labels,
        start_hour=event_start_hour,
        output_dir=output_dir,
        event_name=event_name
    )
    print(f"  Generated {len(vis_files)} visualisation files")
    
    # Step 4: Generate report
    print("\nStep 4: Generating report...")
    report_file = f"{output_dir}/thermal_comfort_report.txt"
    summary = generate_comfort_report(
        baseline_df=baseline_df,
        modified_df=modified_df,
        building_cols=building_cols,
        start_hour=event_start_hour,
        threshold_results=threshold_results,
        output_file=report_file,
        event_name=event_name
    )
    print(f"  Report saved to: {report_file}")
    
    # Step 5: Print summary
    print("\nSummary:")
    print(f"  Average temperature change: {summary['temperature_change']['average']:.2f}°C")
    print(f"  Peak temperature change: {summary['temperature_change']['peak']:.2f}°C")
    print(f"\nAll outputs saved to: {output_dir}")


if __name__ == "__main__":
    print("Thermal Comfort Analysis Examples")
    print("=" * 60)
    
    # Run example (comment out others as needed)
    # example_basic_analysis()
    # example_generate_visualisations()
    # example_custom_building_types()
    # example_custom_thresholds()
    example_complete_workflow()

