"""
IDF Modification Tools
Functions for modifying EnergyPlus IDF files programmatically.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from eppy.modeleditor import IDF


def modify_idf_hvac_schedule(
    idf_path: str,
    output_path: str,
    idd_file: str,
    schedule_action: str = "disable_cooling",
    start_month: int = 7,
    start_day: int = 15,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    schedule_name: Optional[str] = None,
    target_version: str = "25.1.0"
) -> Dict:
    """
    Modify IDF file HVAC schedule to simulate blackout or outage scenarios.
    
    This function creates or modifies a schedule that controls HVAC system
    availability, useful for simulating power outages during extreme weather events.
    
    Args:
        idf_path: Path to the source IDF file
        output_path: Path where the modified IDF will be saved
        idd_file: Path to the Energy+.idd file
        schedule_action: Type of HVAC modification:
            - "disable_cooling": Disable cooling systems
            - "disable_heating": Disable heating systems
            - "disable_all": Disable all HVAC systems
            - "enable_all": Enable all HVAC systems (restore normal operation)
        start_month: Month when the schedule change begins (1-12)
        start_day: Day when the schedule change begins (1-31)
        end_month: Month when the schedule change ends (optional, None means until end of year)
        end_day: Day when the schedule change ends (optional)
        schedule_name: Custom name for the created schedule (optional)
        target_version: EnergyPlus version to set in the IDF file
    
    Returns:
        Dictionary containing:
            - success: Whether the operation succeeded
            - idf_file: Original IDF path
            - output_file: Modified IDF path
            - schedule_name: Name of the created/modified schedule
            - schedule_action: Action performed
            - start_date: Start date as "MM/DD"
            - end_date: End date as "MM/DD" or "End of year"
            - systems_modified: Number of HVAC systems modified
            - message: Descriptive message
    """
    try:
        # Set IDD file
        IDF.setiddname(idd_file)
        
        # Load IDF
        idf = IDF(idf_path)
        
        # Upgrade version if specified
        version_obj = idf.idfobjects.get('VERSION', [])
        if version_obj:
            version_obj[0].Version_Identifier = target_version
        
        # Determine schedule name
        if schedule_name is None:
            action_map = {
                "disable_cooling": "Cooling_Outage_Schedule",
                "disable_heating": "Heating_Outage_Schedule",
                "disable_all": "HVAC_Outage_Schedule",
                "enable_all": "HVAC_Enable_Schedule"
            }
            schedule_name = action_map.get(schedule_action, "Custom_HVAC_Schedule")
        
        # Determine end date
        if end_month is None:
            end_month = 12
            end_day = 31
        elif end_day is None:
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            end_day = days_in_month[end_month - 1]
        
        # Create schedule
        schedule_created = _create_hvac_schedule(
            idf=idf,
            schedule_name=schedule_name,
            start_month=start_month,
            start_day=start_day,
            end_month=end_month,
            end_day=end_day,
            schedule_action=schedule_action
        )
        
        # Apply schedule to HVAC systems
        systems_modified = _apply_schedule_to_hvac_systems(
            idf=idf,
            schedule_name=schedule_name,
            schedule_action=schedule_action
        )
        
        # Ensure zone temperature output is included
        _add_zone_temperature_output(idf)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save modified IDF
        idf.save(output_path)
        
        # Format dates for output
        start_date_str = f"{start_month:02d}/{start_day:02d}"
        end_date_str = f"{end_month:02d}/{end_day:02d}" if end_month != 12 or end_day != 31 else "End of year"
        
        return {
            "success": True,
            "idf_file": str(idf_path),
            "output_file": str(output_path),
            "schedule_name": schedule_name,
            "schedule_action": schedule_action,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "systems_modified": systems_modified,
            "message": f"Successfully modified {systems_modified} HVAC system(s) with {schedule_action} from {start_date_str} to {end_date_str}"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "idf_file": str(idf_path),
            "output_file": str(output_path),
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": f"Failed to modify IDF: {str(e)}"
        }


def batch_modify_idf_hvac_schedule(
    idf_directory: str,
    output_directory: str,
    idd_file: str,
    schedule_action: str = "disable_cooling",
    start_month: int = 7,
    start_day: int = 15,
    end_month: Optional[int] = None,
    end_day: Optional[int] = None,
    schedule_name: Optional[str] = None,
    target_version: str = "25.1.0",
    max_buildings: Optional[int] = None
) -> Dict:
    """
    Batch modify multiple IDF files in a directory.
    
    Args:
        idf_directory: Directory containing IDF files to modify
        output_directory: Directory where modified IDF files will be saved
        idd_file: Path to the Energy+.idd file
        schedule_action: Type of HVAC modification (see modify_idf_hvac_schedule)
        start_month: Month when the schedule change begins (1-12)
        start_day: Day when the schedule change begins (1-31)
        end_month: Month when the schedule change ends (optional)
        end_day: Day when the schedule change ends (optional)
        schedule_name: Custom name for the created schedule (optional)
        target_version: EnergyPlus version to set in the IDF files
        max_buildings: Maximum number of buildings to process (for testing)
    
    Returns:
        Dictionary containing:
            - success: Whether the batch operation succeeded
            - total_buildings: Total number of IDF files found
            - successful_modifications: Number of successfully modified files
            - failed_modifications: Number of failed modifications
            - results: List of individual modification results
    """
    try:
        # Find all IDF files
        idf_files = sorted(Path(idf_directory).glob("*.idf"))
        
        if max_buildings is not None:
            idf_files = idf_files[:max_buildings]
        
        total_buildings = len(idf_files)
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)
        
        results = []
        successful_count = 0
        failed_count = 0
        
        for idx, idf_path in enumerate(idf_files, 1):
            output_path = Path(output_directory) / idf_path.name
            
            print(f"[{idx}/{total_buildings}] Processing {idf_path.name}...")
            
            result = modify_idf_hvac_schedule(
                idf_path=str(idf_path),
                output_path=str(output_path),
                idd_file=idd_file,
                schedule_action=schedule_action,
                start_month=start_month,
                start_day=start_day,
                end_month=end_month,
                end_day=end_day,
                schedule_name=schedule_name,
                target_version=target_version
            )
            
            result["index"] = idx
            result["total"] = total_buildings
            results.append(result)
            
            if result["success"]:
                successful_count += 1
            else:
                failed_count += 1
        
        return {
            "success": True,
            "total_buildings": total_buildings,
            "successful_modifications": successful_count,
            "failed_modifications": failed_count,
            "success_rate": f"{successful_count}/{total_buildings} ({successful_count/total_buildings*100:.1f}%)" if total_buildings > 0 else "0/0 (0.0%)",
            "results": results
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": f"Batch modification failed: {str(e)}"
        }


def _create_hvac_schedule(
    idf: IDF,
    schedule_name: str,
    start_month: int,
    start_day: int,
    end_month: int,
    end_day: int,
    schedule_action: str
) -> bool:
    """
    Create a Schedule:Compact object in the IDF.
    
    Args:
        idf: The IDF object
        schedule_name: Name for the schedule
        start_month: Start month (1-12)
        start_day: Start day (1-31)
        end_month: End month (1-12)
        end_day: End day (1-31)
        schedule_action: Action to perform (disable_cooling, disable_heating, etc.)
    
    Returns:
        True if schedule was created, False if it already exists
    """
    # Check if schedule already exists
    existing_schedules = idf.idfobjects.get('SCHEDULE:COMPACT', [])
    schedule_exists = any(sch.Name == schedule_name for sch in existing_schedules)
    
    if schedule_exists:
        # Remove existing schedule to recreate it
        for sch in existing_schedules:
            if sch.Name == schedule_name:
                idf.removeidfobject(sch)
    
    # Helper function to convert month/day to day of year
    def to_day_of_year(month: int, day: int) -> int:
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return sum(days_in_month[:month-1]) + day
    
    # Calculate day of year for start and end
    start_doy = to_day_of_year(start_month, start_day)
    end_doy = to_day_of_year(end_month, end_day)
    
    # Determine schedule values based on action
    if schedule_action == "enable_all":
        # Always enabled
        value_before = "1"
        value_during = "1"
        value_after = "1"
    else:
        # Enabled before and after, disabled during
        value_before = "1"
        value_during = "0"
        value_after = "1"
    
    # Create the schedule
    new_schedule = idf.newidfobject('SCHEDULE:COMPACT')
    new_schedule.Name = schedule_name
    new_schedule.Schedule_Type_Limits_Name = "Fraction"
    
    # Build schedule fields
    field_idx = 1
    
    for month in range(1, 13):
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for day in range(1, days_in_month[month-1] + 1):
            current_doy = to_day_of_year(month, day)
            
            # Determine value for this day
            if current_doy < start_doy:
                value = value_before
            elif start_doy <= current_doy <= end_doy:
                value = value_during
            else:
                value = value_after
            
            # Add schedule entries
            setattr(new_schedule, f'Field_{field_idx}', f"Through: {month:02d}/{day:02d}")
            field_idx += 1
            setattr(new_schedule, f'Field_{field_idx}', "For: AllDays")
            field_idx += 1
            setattr(new_schedule, f'Field_{field_idx}', "Until: 24:00")
            field_idx += 1
            setattr(new_schedule, f'Field_{field_idx}', value)
            field_idx += 1
    
    return True


def _apply_schedule_to_hvac_systems(
    idf: IDF,
    schedule_name: str,
    schedule_action: str
) -> int:
    """
    Apply the created schedule to HVAC systems in the IDF.
    
    Args:
        idf: The IDF object
        schedule_name: Name of the schedule to apply
        schedule_action: Type of action (determines which field to modify)
    
    Returns:
        Number of systems modified
    """
    modified_count = 0
    
    # Try HVACTemplate objects first
    ideal_loads_systems = idf.idfobjects.get('HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM', [])
    
    # If no HVACTemplate objects, try regular objects
    if not ideal_loads_systems:
        ideal_loads_systems = idf.idfobjects.get('ZONEHVAC:IDEALLOADSAIRSYSTEM', [])
    
    # Apply schedule based on action type
    for system in ideal_loads_systems:
        try:
            if schedule_action == "disable_cooling" or schedule_action == "disable_all":
                if hasattr(system, 'Cooling_Availability_Schedule_Name'):
                    system.Cooling_Availability_Schedule_Name = schedule_name
                    modified_count += 1
            
            if schedule_action == "disable_heating" or schedule_action == "disable_all":
                if hasattr(system, 'Heating_Availability_Schedule_Name'):
                    system.Heating_Availability_Schedule_Name = schedule_name
                    modified_count += 1
            
            if schedule_action == "enable_all":
                # Set to blank or a default "always on" schedule
                if hasattr(system, 'Cooling_Availability_Schedule_Name'):
                    system.Cooling_Availability_Schedule_Name = ""
                if hasattr(system, 'Heating_Availability_Schedule_Name'):
                    system.Heating_Availability_Schedule_Name = ""
                modified_count += 1
                
        except Exception as e:
            # Continue if a particular system can't be modified
            pass
    
    return modified_count


def _add_zone_temperature_output(idf: IDF) -> bool:
    """
    Ensure zone mean air temperature output variable is included.
    
    Args:
        idf: The IDF object
    
    Returns:
        True if output was added, False if it already exists
    """
    output_vars = idf.idfobjects.get('OUTPUT:VARIABLE', [])
    
    # Check if zone temperature output already exists
    has_zone_temp_output = any(
        var.Variable_Name.lower() == 'zone mean air temperature' 
        for var in output_vars if hasattr(var, 'Variable_Name')
    )
    
    if not has_zone_temp_output:
        output_var = idf.newidfobject('OUTPUT:VARIABLE')
        output_var.Key_Value = '*'
        output_var.Variable_Name = 'Zone Mean Air Temperature'
        output_var.Reporting_Frequency = 'Hourly'
        return True
    
    return False

