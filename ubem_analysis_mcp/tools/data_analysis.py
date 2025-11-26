"""
Data Analysis Tools
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def extract_zone_temperatures(result_dir: str) -> Optional[List[float]]:
    """
    Extract zone mean air temperatures from EnergyPlus output CSV.
    
    Args:
        result_dir: Directory containing eplusout.csv
        
    Returns:
        List of hourly average temperatures or None if failed
    """
    try:
        csv_file = os.path.join(result_dir, 'eplusout.csv')
        if not os.path.exists(csv_file):
            return None
        
        df = pd.read_csv(csv_file)
        temp_columns = [col for col in df.columns if 'Zone Mean Air Temperature' in col]
        
        if not temp_columns:
            return None
        
        zone_temps = df[temp_columns]
        avg_temps = zone_temps.mean(axis=1)
        return avg_temps.tolist()
        
    except Exception:
        return None


def analyze_simulation_results(
    baseline_results_dir: str,
    modified_results_dir: Optional[str] = None
) -> Dict:
    """
    Analyze simulation results and calculate temperature statistics.
    
    Args:
        baseline_results_dir: Directory containing baseline simulation results
        modified_results_dir: Directory containing modified simulation results (optional)
        
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
            baseline_temps = extract_zone_temperatures(baseline_dir)
            
            baseline_avg = np.mean(baseline_temps) if baseline_temps else np.nan
            
            # Extract modified temperatures if directory provided
            modified_avg = np.nan
            if modified_results_dir:
                modified_dir = os.path.join(modified_results_dir, building_name)
                if os.path.exists(modified_dir):
                    modified_temps = extract_zone_temperatures(modified_dir)
                    modified_avg = np.mean(modified_temps) if modified_temps else np.nan
            
            # Calculate temperature increase
            temp_increase = modified_avg - baseline_avg if (not np.isnan(baseline_avg) and not np.isnan(modified_avg)) else np.nan
            
            comparison_data.append({
                'Building': building_name,
                'Baseline_Annual_Avg_Temp_C': round(baseline_avg, 2) if not np.isnan(baseline_avg) else None,
                'Modified_Annual_Avg_Temp_C': round(modified_avg, 2) if not np.isnan(modified_avg) else None,
                'Temperature_Increase_C': round(temp_increase, 2) if not np.isnan(temp_increase) else None
            })
        
        # Calculate statistics
        df_comparison = pd.DataFrame(comparison_data)
        valid_data = df_comparison.dropna(subset=['Temperature_Increase_C'])
        
        result = {
            "success": True,
            "total_buildings": len(df_comparison),
            "valid_comparisons": len(valid_data),
            "statistics": {
                "mean_increase": float(valid_data['Temperature_Increase_C'].mean()) if len(valid_data) > 0 else None,
                "median_increase": float(valid_data['Temperature_Increase_C'].median()) if len(valid_data) > 0 else None,
                "std_increase": float(valid_data['Temperature_Increase_C'].std()) if len(valid_data) > 0 else None,
                "min_increase": float(valid_data['Temperature_Increase_C'].min()) if len(valid_data) > 0 else None,
                "max_increase": float(valid_data['Temperature_Increase_C'].max()) if len(valid_data) > 0 else None
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
    output_csv: str
) -> Dict:
    """
    Generate hourly temperature CSV from simulation results.
    
    Args:
        results_dir: Directory containing simulation results
        output_csv: Output CSV file path
        
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
            temps = extract_zone_temperatures(result_dir)
            
            if temps:
                all_hourly_temps[building_name] = temps
        
        # Create DataFrame
        df_hourly = pd.DataFrame(all_hourly_temps)
        df_hourly.insert(0, 'Hour', range(1, len(df_hourly) + 1))
        
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
    output_csv: str
) -> Dict:
    """
    Create comparison CSV between baseline and modified scenarios.
    
    Args:
        baseline_results_dir: Directory containing baseline results
        modified_results_dir: Directory containing modified results
        output_csv: Output CSV file path
        
    Returns:
        Dictionary containing creation status
    """
    try:
        # Analyze results
        analysis = analyze_simulation_results(baseline_results_dir, modified_results_dir)
        
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

