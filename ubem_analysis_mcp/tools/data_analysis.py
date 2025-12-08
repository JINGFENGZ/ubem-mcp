"""
Data Analysis Tools
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def extract_zone_temperatures(
    result_dir: str,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature'
) -> Optional[List[float]]:
    """
    Extract zone mean air temperatures from EnergyPlus output CSV.
    
    Args:
        result_dir: Directory containing output CSV
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns 
                                   (default: 'Zone Mean Air Temperature')
        
    Returns:
        List of hourly average temperatures or None if failed
    """
    try:
        csv_file = os.path.join(result_dir, output_csv_name)
        if not os.path.exists(csv_file):
            return None
        
        df = pd.read_csv(csv_file)
        temp_columns = [col for col in df.columns if temperature_column_pattern in col]
        
        if not temp_columns:
            return None
        
        zone_temps = df[temp_columns]
        avg_temps = zone_temps.mean(axis=1)
        return avg_temps.tolist()
        
    except Exception:
        return None


def analyze_simulation_results(
    baseline_results_dir: str,
    modified_results_dir: Optional[str] = None,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    temperature_unit: str = 'C'
) -> Dict:
    """
    Analyze simulation results and calculate temperature statistics.
    
    Args:
        baseline_results_dir: Directory containing baseline simulation results
        modified_results_dir: Directory containing modified simulation results (optional)
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns
        temperature_unit: Temperature unit for display (default: 'C')
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Get all result directories
        baseline_dirs = sorted([
            d for d in os.listdir(baseline_results_dir)
            if os.path.isdir(os.path.join(baseline_results_dir, d))
        ])
        
        comparison_data = []
        
        for building_name in baseline_dirs:
            # Extract baseline temperatures
            baseline_dir = os.path.join(baseline_results_dir, building_name)
            baseline_temps = extract_zone_temperatures(
                baseline_dir, output_csv_name, temperature_column_pattern
            )
            
            baseline_avg = np.mean(baseline_temps) if baseline_temps else np.nan
            
            # Extract modified temperatures if directory provided
            modified_avg = np.nan
            if modified_results_dir:
                modified_dir = os.path.join(modified_results_dir, building_name)
                if os.path.exists(modified_dir):
                    modified_temps = extract_zone_temperatures(
                        modified_dir, output_csv_name, temperature_column_pattern
                    )
                    modified_avg = np.mean(modified_temps) if modified_temps else np.nan
            
            # Calculate temperature increase
            temp_increase = modified_avg - baseline_avg if (not np.isnan(baseline_avg) and not np.isnan(modified_avg)) else np.nan
            
            comparison_data.append({
                'Building': building_name,
                f'Baseline_Annual_Avg_Temp_{temperature_unit}': round(baseline_avg, 2) if not np.isnan(baseline_avg) else None,
                f'Modified_Annual_Avg_Temp_{temperature_unit}': round(modified_avg, 2) if not np.isnan(modified_avg) else None,
                f'Temperature_Increase_{temperature_unit}': round(temp_increase, 2) if not np.isnan(temp_increase) else None
            })
        
        # Calculate statistics
        df_comparison = pd.DataFrame(comparison_data)
        increase_col = f'Temperature_Increase_{temperature_unit}'
        valid_data = df_comparison.dropna(subset=[increase_col])
        
        result = {
            "success": True,
            "total_buildings": len(df_comparison),
            "valid_comparisons": len(valid_data),
            "statistics": {
                "mean_increase": float(valid_data[increase_col].mean()) if len(valid_data) > 0 else None,
                "median_increase": float(valid_data[increase_col].median()) if len(valid_data) > 0 else None,
                "std_increase": float(valid_data[increase_col].std()) if len(valid_data) > 0 else None,
                "min_increase": float(valid_data[increase_col].min()) if len(valid_data) > 0 else None,
                "max_increase": float(valid_data[increase_col].max()) if len(valid_data) > 0 else None
            },
            "buildings": comparison_data
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_hourly_csv(
    results_dir: str,
    output_csv: str,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    time_column_name: str = 'Hour'
) -> Dict:
    """
    Generate hourly temperature CSV from simulation results.
    
    Args:
        results_dir: Directory containing simulation results
        output_csv: Output CSV file path
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns
        time_column_name: Name of the time column in output (default: 'Hour')
        
    Returns:
        Dictionary containing generation status
    """
    try:
        # Get all result directories
        result_dirs = sorted([
            d for d in os.listdir(results_dir)
            if os.path.isdir(os.path.join(results_dir, d))
        ])
        
        # Dictionary to store hourly temperatures
        all_hourly_temps = {}
        
        for building_name in result_dirs:
            result_dir = os.path.join(results_dir, building_name)
            temps = extract_zone_temperatures(
                result_dir, output_csv_name, temperature_column_pattern
            )
            
            if temps:
                all_hourly_temps[building_name] = temps
        
        # Create DataFrame
        df_hourly = pd.DataFrame(all_hourly_temps)
        df_hourly.insert(0, time_column_name, range(1, len(df_hourly) + 1))
        
        # Save to CSV
        df_hourly.to_csv(output_csv, index=False)
        
        file_size_mb = os.path.getsize(output_csv) / (1024 * 1024)
        
        return {
            "success": True,
            "output_file": output_csv,
            "total_hours": len(df_hourly),
            "total_buildings": len(all_hourly_temps),
            "file_size_mb": round(file_size_mb, 2),
            "data_points": len(df_hourly) * len(all_hourly_temps)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output_file": output_csv
        }


def create_comparison_csv(
    baseline_results_dir: str,
    modified_results_dir: str,
    output_csv: str,
    output_csv_name: str = 'eplusout.csv',
    temperature_column_pattern: str = 'Zone Mean Air Temperature',
    temperature_unit: str = 'C'
) -> Dict:
    """
    Create comparison CSV between baseline and modified scenarios.
    
    Args:
        baseline_results_dir: Directory containing baseline results
        modified_results_dir: Directory containing modified results
        output_csv: Output CSV file path
        output_csv_name: Name of the output CSV file (default: 'eplusout.csv')
        temperature_column_pattern: Pattern to match temperature columns
        temperature_unit: Temperature unit for display (default: 'C')
        
    Returns:
        Dictionary containing creation status
    """
    try:
        # Analyze results
        analysis = analyze_simulation_results(
            baseline_results_dir,
            modified_results_dir,
            output_csv_name,
            temperature_column_pattern,
            temperature_unit
        )
        
        if not analysis["success"]:
            return analysis
        
        # Create DataFrame and save
        df = pd.DataFrame(analysis["buildings"])
        df.to_csv(output_csv, index=False)
        
        file_size_kb = os.path.getsize(output_csv) / 1024
        
        return {
            "success": True,
            "output_file": output_csv,
            "total_buildings": analysis["total_buildings"],
            "valid_comparisons": analysis["valid_comparisons"],
            "file_size_kb": round(file_size_kb, 2),
            "statistics": analysis["statistics"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output_file": output_csv
        }

