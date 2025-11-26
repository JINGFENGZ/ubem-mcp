"""
Configuration for UBEM Analysis MCP Server

IMPORTANT: Update these paths according to your local installation
"""

import os
from pathlib import Path

# Get configuration from environment variables or use defaults
def get_project_root():
    """Get project root from environment or use current directory"""
    return Path(os.getenv("UBEM_PROJECT_ROOT", Path.cwd()))

def get_energyplus_path():
    """Get EnergyPlus installation path from environment"""
    default_paths = {
        "win32": r"C:\EnergyPlusV25-1-0",
        "darwin": "/Applications/EnergyPlus-25-1-0",
        "linux": "/usr/local/EnergyPlus-25-1-0"
    }
    import sys
    platform = sys.platform
    if platform.startswith("linux"):
        platform = "linux"
    elif platform == "darwin":
        platform = "darwin"
    else:
        platform = "win32"
    
    return Path(os.getenv("ENERGYPLUS_ROOT", default_paths.get(platform, "")))

# Default paths
PROJECT_ROOT = get_project_root()
ENERGYPLUS_ROOT = get_energyplus_path()

# EnergyPlus executables
IDD_FILE = ENERGYPLUS_ROOT / "Energy+.idd"
ENERGYPLUS_EXE = ENERGYPLUS_ROOT / "energyplus"
EXPAND_OBJECTS_EXE = ENERGYPLUS_ROOT / "ExpandObjects"

# Add .exe extension on Windows
if os.name == 'nt':
    ENERGYPLUS_EXE = ENERGYPLUS_ROOT / "energyplus.exe"
    EXPAND_OBJECTS_EXE = ENERGYPLUS_ROOT / "ExpandObjects.exe"

# Project directories (relative to PROJECT_ROOT)
BASELINE_DIR = PROJECT_ROOT / "baseline_models"
MODIFIED_DIR = PROJECT_ROOT / "modified_models"
WEATHER_DIR = PROJECT_ROOT / "weather"
RESULTS_BASELINE_DIR = PROJECT_ROOT / "simulation_results_baseline"
RESULTS_MODIFIED_DIR = PROJECT_ROOT / "simulation_results_modified"

# Default weather file (update with your weather file)
WEATHER_FILE = WEATHER_DIR / "weather_file.epw"

# Output files
TEMPERATURE_COMPARISON_CSV = PROJECT_ROOT / "temperature_comparison.csv"
HOURLY_BASELINE_CSV = PROJECT_ROOT / "hourly_temperatures_baseline.csv"
HOURLY_MODIFIED_CSV = PROJECT_ROOT / "hourly_temperatures_modified.csv"

def get_config():
    """Get configuration dictionary"""
    return {
        "project_root": str(PROJECT_ROOT),
        "idd_file": str(IDD_FILE),
        "energyplus_exe": str(ENERGYPLUS_EXE),
        "expand_objects_exe": str(EXPAND_OBJECTS_EXE),
        "baseline_dir": str(BASELINE_DIR),
        "modified_dir": str(MODIFIED_DIR),
        "weather_dir": str(WEATHER_DIR),
        "weather_file": str(WEATHER_FILE),
        "results_baseline_dir": str(RESULTS_BASELINE_DIR),
        "results_modified_dir": str(RESULTS_MODIFIED_DIR),
        "temperature_comparison_csv": str(TEMPERATURE_COMPARISON_CSV),
        "hourly_baseline_csv": str(HOURLY_BASELINE_CSV),
        "hourly_modified_csv": str(HOURLY_MODIFIED_CSV)
    }

def validate_config():
    """Validate that required paths exist"""
    errors = []
    
    if not IDD_FILE.exists():
        errors.append(f"IDD file not found: {IDD_FILE}")
    
    if not ENERGYPLUS_EXE.exists():
        errors.append(f"EnergyPlus executable not found: {ENERGYPLUS_EXE}")
    
    if errors:
        raise FileNotFoundError("\n".join(errors) + 
            "\n\nPlease update paths in config.py or set environment variables:\n" +
            "- UBEM_PROJECT_ROOT: Your project root directory\n" +
            "- ENERGYPLUS_ROOT: EnergyPlus installation directory")
    
    return True

