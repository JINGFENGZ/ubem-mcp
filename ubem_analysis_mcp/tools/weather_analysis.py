"""
Weather Data Analysis Tools
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


def analyze_epw_hottest_days(epw_file_path: str, top_n: int = 3) -> Dict:
    """
    Analyze EPW weather file to identify the hottest days based on daily average dry bulb temperature.
    
    Args:
        epw_file_path: Path to the EPW weather file
        top_n: Number of hottest days to identify (default: 3)
        
    Returns:
        Dictionary containing hottest days information including:
        - success: bool
        - top_hottest_days: List of hottest days with temperature data
        - earliest_hot_day: Earliest day among the hottest days
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
        
        # Sort by average temperature
        sorted_days = sorted(daily_avg.items(), key=lambda x: x[1], reverse=True)
        
        # Get top N hottest days
        hottest_days = sorted_days[:top_n]
        
        # Find the earliest day among the hottest days
        def to_day_of_year(month, day):
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            return sum(days_in_month[:month-1]) + day
        
        hottest_dates = [(m, d) for (m, d), _ in hottest_days]
        hottest_doy = [(to_day_of_year(m, d), m, d) for m, d in hottest_dates]
        hottest_doy.sort()
        
        earliest_month, earliest_day = hottest_doy[0][1], hottest_doy[0][2]
        
        # Prepare result
        result = {
            "success": True,
            "epw_file": epw_file_path,
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
                "description": "Earliest day among the top hottest days"
            }
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

