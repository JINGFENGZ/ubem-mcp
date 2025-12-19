"""
Weather Data Analysis Tools
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


def analyze_epw_hottest_days(epw_file_path: str, top_n: int = 3) -> Dict:
    """
    Analyse EPW weather file to identify the hottest consecutive days sequence based on daily average dry bulb temperature.
    
    This function finds the consecutive N-day period with the highest average temperature across the year.
    
    Args:
        epw_file_path: Path to the EPW weather file
        top_n: Number of consecutive days in the heatwave (default: 3)
        
    Returns:
        Dictionary containing hottest consecutive days information including:
        - success: bool
        - top_hottest_days: List of consecutive hottest days with temperature data
        - earliest_hot_day: The first day of the hottest consecutive sequence
    """
    try:
        # Read EPW data (skip first 8 header lines)
        df = pd.read_csv(epw_file_path, skiprows=8, header=None)
        
        # Extract relevant columns: Month (1), Day (2), Hour (3), Dry Bulb Temperature (6)
        temperatures = []
        dates = []
        
        for _, row in df.iterrows():
            month = int(row[1])
            day = int(row[2])
            hour = int(row[3])
            temp = float(row[6])
            
            temperatures.append(temp)
            dates.append((month, day, hour))
        
        # Calculate daily average temperatures
        daily_temps = defaultdict(list)
        for temp, (month, day, hour) in zip(temperatures, dates):
            date_key = (month, day)
            daily_temps[date_key].append(temp)
        
        # Calculate average and max temperature for each day
        daily_avg = {}
        daily_max = {}
        for date_key, temps in daily_temps.items():
            daily_avg[date_key] = np.mean(temps)
            daily_max[date_key] = np.max(temps)
        
        # Convert to day-of-year based list for consecutive search
        def to_day_of_year(month, day):
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            return sum(days_in_month[:month-1]) + day
        
        def from_day_of_year(doy):
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            month = 1
            remaining = doy
            for i, days in enumerate(days_in_month):
                if remaining <= days:
                    return (i + 1, remaining)
                remaining -= days
                month += 1
            return (12, 31)  # fallback
        
        # Create ordered list of all days with temperatures
        all_days = []
        for (month, day), avg_temp in daily_avg.items():
            doy = to_day_of_year(month, day)
            all_days.append((doy, month, day, avg_temp, daily_max[(month, day)]))
        all_days.sort()
        
        # Find consecutive N days with highest average temperature
        best_avg = -999
        best_start_idx = 0
        
        for i in range(len(all_days) - top_n + 1):
            # Check if these are consecutive days
            is_consecutive = True
            for j in range(top_n - 1):
                if all_days[i + j + 1][0] != all_days[i + j][0] + 1:
                    is_consecutive = False
                    break
            
            if is_consecutive:
                # Calculate average temperature of this consecutive sequence
                avg_temp = np.mean([all_days[i + j][3] for j in range(top_n)])
                if avg_temp > best_avg:
                    best_avg = avg_temp
                    best_start_idx = i
        
        # Extract the hottest consecutive days
        hottest_days = []
        for j in range(top_n):
            doy, month, day, avg_temp, max_temp = all_days[best_start_idx + j]
            hottest_days.append(((month, day), avg_temp))
        
        # The earliest day is the first day of the sequence
        earliest_month, earliest_day = hottest_days[0][0]
        
        # Prepare result
        result = {
            "success": True,
            "epw_file": epw_file_path,
            "consecutive_days": top_n,
            "top_hottest_days": [
                {
                    "rank": i + 1,
                    "month": int(month),
                    "day": int(day),
                    "date": f"{month:02d}/{day:02d}",
                    "average_temperature": float(avg_temp),
                    "maximum_temperature": float(daily_max[(month, day)])
                }
                for i, ((month, day), avg_temp) in enumerate(hottest_days)
            ],
            "earliest_hot_day": {
                "month": int(earliest_month),
                "day": int(earliest_day),
                "date": f"{earliest_month:02d}/{earliest_day:02d}",
                "description": f"First day of the hottest {top_n} consecutive days sequence"
            },
            "sequence_average_temperature": float(best_avg)
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "epw_file": epw_file_path
        }


def get_hottest_day_date(epw_file_path: str, top_n: int = 3) -> Optional[Tuple[int, int]]:
    """
    Get the earliest hottest day as a tuple (month, day).
    
    Args:
        epw_file_path: Path to EPW file
        top_n: Number of hottest days to consider
        
    Returns:
        Tuple of (month, day) or None if failed
    """
    result = analyze_epw_hottest_days(epw_file_path, top_n)
    if result["success"]:
        earliest = result["earliest_hot_day"]
        return (earliest["month"], earliest["day"])
    return None

