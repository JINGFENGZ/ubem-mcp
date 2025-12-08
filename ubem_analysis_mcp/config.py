"""
Configuration for UBEM Analysis MCP Server

This module provides helper functions to locate EnergyPlus installation.
All paths are configurable via environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_energyplus_root() -> Optional[Path]:
    """
    Get EnergyPlus installation path from environment variable.
    
    Environment variable: ENERGYPLUS_ROOT
    
    Returns:
        Path to EnergyPlus installation or None if not set
    """
    ep_root = os.getenv("ENERGYPLUS_ROOT")
    if ep_root:
        return Path(ep_root)
    
    # Try common default locations
    if sys.platform == "win32":
        common_paths = [
            r"C:\EnergyPlusV25-1-0",
            r"C:\EnergyPlusV24-2-0",
            r"C:\EnergyPlusV23-2-0"
        ]
    elif sys.platform == "darwin":
        common_paths = [
            "/Applications/EnergyPlus-25-1-0",
            "/Applications/EnergyPlus-24-2-0",
            "/Applications/EnergyPlus-23-2-0"
        ]
    else:  # Linux
        common_paths = [
            "/usr/local/EnergyPlus-25-1-0",
            "/usr/local/EnergyPlus-24-2-0",
            "/usr/local/EnergyPlus-23-2-0"
        ]
    
    # Check if any common path exists
    for path in common_paths:
        if Path(path).exists():
            return Path(path)
    
    return None


def get_energyplus_executable(ep_root: Optional[Path] = None) -> Optional[str]:
    """
    Get EnergyPlus executable path.
    
    Args:
        ep_root: EnergyPlus root directory (optional)
        
    Returns:
        Full path to energyplus executable or None
    """
    if not ep_root:
        ep_root = get_energyplus_root()
    
    if not ep_root or not ep_root.exists():
        return None
    
    exe_name = "energyplus.exe" if os.name == 'nt' else "energyplus"
    exe_path = ep_root / exe_name
    
    return str(exe_path) if exe_path.exists() else None


def get_expand_objects_executable(ep_root: Optional[Path] = None) -> Optional[str]:
    """
    Get ExpandObjects executable path.
    
    Args:
        ep_root: EnergyPlus root directory (optional)
        
    Returns:
        Full path to ExpandObjects executable or None
    """
    if not ep_root:
        ep_root = get_energyplus_root()
    
    if not ep_root or not ep_root.exists():
        return None
    
    exe_name = "ExpandObjects.exe" if os.name == 'nt' else "ExpandObjects"
    exe_path = ep_root / exe_name
    
    return str(exe_path) if exe_path.exists() else None


def get_idd_file(ep_root: Optional[Path] = None) -> Optional[str]:
    """
    Get Energy+.idd file path.
    
    Args:
        ep_root: EnergyPlus root directory (optional)
        
    Returns:
        Full path to Energy+.idd file or None
    """
    if not ep_root:
        ep_root = get_energyplus_root()
    
    if not ep_root or not ep_root.exists():
        return None
    
    idd_path = ep_root / "Energy+.idd"
    
    return str(idd_path) if idd_path.exists() else None


def get_config() -> dict:
    """
    Get minimal configuration dictionary with auto-detected EnergyPlus paths.
    
    This is a convenience function that returns basic configuration.
    All parameters can be overridden when calling MCP tools.
    
    Returns:
        Dictionary with EnergyPlus paths (may contain None values)
    """
    ep_root = get_energyplus_root()
    
    return {
        "energyplus_root": str(ep_root) if ep_root else None,
        "energyplus_exe": get_energyplus_executable(ep_root),
        "expand_objects_exe": get_expand_objects_executable(ep_root),
        "idd_file": get_idd_file(ep_root)
    }

