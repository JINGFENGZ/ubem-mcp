"""
EnergyPlus Simulation Tools
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def run_energyplus_simulation(
    idf_path: str,
    weather_file: str,
    output_dir: str,
    energyplus_exe: str,
    expand_objects_exe: Optional[str] = None,
    timeout: int = 600
) -> Dict:
    """
    Run EnergyPlus simulation for a single IDF file.
    
    Args:
        idf_path: Path to IDF file
        weather_file: Path to weather file
        output_dir: Output directory for simulation results
        energyplus_exe: Path to EnergyPlus executable
        expand_objects_exe: Path to ExpandObjects executable (optional)
        timeout: Simulation timeout in seconds (default: 600)
        
    Returns:
        Dictionary containing simulation status
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Run ExpandObjects if needed and executable is provided
        if expand_objects_exe and os.path.exists(expand_objects_exe):
            try:
                # Copy IDF to output directory
                import shutil
                temp_idf = os.path.join(output_dir, "in.idf")
                shutil.copy(idf_path, temp_idf)
                
                # Run ExpandObjects
                expand_cmd = [expand_objects_exe]
                subprocess.run(
                    expand_cmd,
                    cwd=output_dir,
                    capture_output=True,
                    timeout=300
                )
                
                # Use expanded.idf if it exists
                expanded_idf = os.path.join(output_dir, "expanded.idf")
                if os.path.exists(expanded_idf):
                    idf_path = expanded_idf
            except Exception as e:
                # Continue with original IDF if ExpandObjects fails
                pass
        
        # Run EnergyPlus
        cmd = [
            energyplus_exe,
            '-w', weather_file,
            '-d', output_dir,
            '-x',  # No XML output
            '-r',  # No SVG output
            idf_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Check if simulation was successful
        eplusout_csv = os.path.join(output_dir, 'eplusout.csv')
        success = os.path.exists(eplusout_csv)
        
        return {
            "success": success,
            "idf_file": os.path.basename(idf_path),
            "output_directory": output_dir,
            "has_csv_output": success,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "idf_file": os.path.basename(idf_path),
            "error": f"Simulation timeout (>{timeout}s)"
        }
    except Exception as e:
        return {
            "success": False,
            "idf_file": os.path.basename(idf_path),
            "error": str(e)
        }


def batch_simulate_buildings(
    idf_directory: str,
    weather_file: str,
    output_base_dir: str,
    energyplus_exe: str,
    expand_objects_exe: Optional[str] = None,
    max_buildings: Optional[int] = None,
    timeout: int = 600
) -> Dict:
    """
    Run EnergyPlus simulations for multiple IDF files in a directory.
    
    Args:
        idf_directory: Directory containing IDF files
        weather_file: Path to weather file
        output_base_dir: Base directory for simulation outputs
        energyplus_exe: Path to EnergyPlus executable
        expand_objects_exe: Path to ExpandObjects executable (optional)
        max_buildings: Maximum number of buildings to simulate (optional)
        timeout: Simulation timeout per building in seconds (default: 600)
        
    Returns:
        Dictionary containing batch simulation results
    """
    try:
        # Get all IDF files
        idf_files = sorted([
            f for f in os.listdir(idf_directory)
            if f.endswith('.idf')
        ])
        
        if max_buildings:
            idf_files = idf_files[:max_buildings]
        
        results = []
        success_count = 0
        
        for i, idf_file in enumerate(idf_files, 1):
            idf_path = os.path.join(idf_directory, idf_file)
            building_name = idf_file.replace('.idf', '')
            output_dir = os.path.join(output_base_dir, building_name)
            
            result = run_energyplus_simulation(
                idf_path,
                weather_file,
                output_dir,
                energyplus_exe,
                expand_objects_exe,
                timeout
            )
            
            result["index"] = i
            result["total"] = len(idf_files)
            results.append(result)
            
            if result["success"]:
                success_count += 1
        
        return {
            "success": True,
            "total_buildings": len(idf_files),
            "successful_simulations": success_count,
            "failed_simulations": len(idf_files) - success_count,
            "success_rate": f"{success_count / len(idf_files) * 100:.1f}%" if idf_files else "0.0%",
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

