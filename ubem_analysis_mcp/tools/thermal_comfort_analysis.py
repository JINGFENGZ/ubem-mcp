# -*- coding: utf-8 -*-
"""
Thermal Comfort Analysis Tools
Analyse the impact of temperature changes on indoor comfort during extreme weather events
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Configure matplotlib with Times New Roman font
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# Default comfort standards (°C)
DEFAULT_COMFORT_RANGES = {
    'optimal': (20, 26),
    'acceptable': (18, 28),
    'slight_warm': (28, 30),
    'moderate_warm': (30, 32),
    'hot': (32, 35),
    'extreme_hot': (35, 100)
}

# Default building type mapping
DEFAULT_BUILDING_TYPE_MAP = {
    '0': 'Lowrise_Domestic',
    '1': 'Midrise_Domestic',
    '2': 'Highrise_Domestic',
    '3': 'Commercial',
    '4': 'Office',
    '5': 'Industry',
    '6': 'Transport',
    '7': 'Administration'
}


def extract_building_label(column_name: str, building_type_map: Dict[str, str]) -> str:
    """
    Extract building label from column name.
    
    Args:
        column_name: Column name from CSV (e.g., 'city_0_10_1980_S0_Idealload')
        building_type_map: Mapping of type ID to building type name
        
    Returns:
        Building label (e.g., 'Lowrise_Domestic_10')
    """
    parts = column_name.split('_')
    if len(parts) >= 3:
        type_id = parts[1]
        building_num = parts[2]
        building_type = building_type_map.get(type_id, f'Type{type_id}')
        return f'{building_type}_{building_num}'
    return column_name


def load_hourly_temperature_data(
    baseline_file: str,
    modified_file: str,
    building_type_map: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], Dict[str, str]]:
    """
    Load baseline and modified hourly temperature data.
    
    Args:
        baseline_file: Path to baseline CSV file
        modified_file: Path to modified CSV file
        building_type_map: Optional custom building type mapping
        
    Returns:
        Tuple of (baseline_df, modified_df, building_cols, building_labels)
    """
    if building_type_map is None:
        building_type_map = DEFAULT_BUILDING_TYPE_MAP
    
    baseline_df = pd.read_csv(baseline_file)
    modified_df = pd.read_csv(modified_file)
    
    # Ensure both files have the same columns
    if list(baseline_df.columns) != list(modified_df.columns):
        raise ValueError("Column mismatch between baseline and modified files")
    
    # Add datetime column (assuming first row is hour 1 of year)
    baseline_df['DateTime'] = [datetime(2020, 1, 1) + timedelta(hours=i) 
                                for i in range(len(baseline_df))]
    modified_df['DateTime'] = [datetime(2020, 1, 1) + timedelta(hours=i) 
                                for i in range(len(modified_df))]
    
    # Get building column names
    building_cols = [col for col in baseline_df.columns if col not in ['Hour', 'DateTime']]
    
    # Create building label mapping
    building_labels = {col: extract_building_label(col, building_type_map) 
                       for col in building_cols}
    
    # Calculate statistics
    baseline_df['Temp_Mean'] = baseline_df[building_cols].mean(axis=1)
    baseline_df['Temp_Min'] = baseline_df[building_cols].min(axis=1)
    baseline_df['Temp_Max'] = baseline_df[building_cols].max(axis=1)
    baseline_df['Temp_Std'] = baseline_df[building_cols].std(axis=1)
    
    modified_df['Temp_Mean'] = modified_df[building_cols].mean(axis=1)
    modified_df['Temp_Min'] = modified_df[building_cols].min(axis=1)
    modified_df['Temp_Max'] = modified_df[building_cols].max(axis=1)
    modified_df['Temp_Std'] = modified_df[building_cols].std(axis=1)
    
    return baseline_df, modified_df, building_cols, building_labels


def analyse_comfort_thresholds(
    baseline_df: pd.DataFrame,
    modified_df: pd.DataFrame,
    building_cols: List[str],
    start_hour: int,
    thresholds: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Analyse comfort threshold breaches.
    
    Args:
        baseline_df: Baseline DataFrame
        modified_df: Modified DataFrame
        building_cols: List of building column names
        start_hour: Hour when the event starts (e.g., heatwave)
        thresholds: Optional custom temperature thresholds (°C)
        
    Returns:
        Dictionary with analysis results
    """
    if thresholds is None:
        thresholds = {
            'comfort_limit': 26,
            'acceptable_limit': 28,
            'health_risk': 30,
            'severe_risk': 35
        }
    
    # Filter to event period
    event_mask = baseline_df['Hour'] >= start_hour
    baseline_event = baseline_df[event_mask]
    modified_event = modified_df[event_mask]
    
    results = {}
    
    for threshold_name, threshold_temp in thresholds.items():
        baseline_breach = (baseline_event[building_cols] > threshold_temp)
        modified_breach = (modified_event[building_cols] > threshold_temp)
        
        baseline_breach_ratio = (baseline_breach.sum(axis=0) / len(baseline_event) * 100)
        modified_breach_ratio = (modified_breach.sum(axis=0) / len(modified_event) * 100)
        
        avg_baseline = baseline_breach_ratio.mean()
        avg_modified = modified_breach_ratio.mean()
        
        # Find first massive breach (>50% buildings)
        baseline_breach_count = baseline_breach.sum(axis=1)
        modified_breach_count = modified_breach.sum(axis=1)
        threshold_buildings = len(building_cols) * 0.5
        
        modified_first_breach = modified_breach_count[modified_breach_count > threshold_buildings]
        
        first_breach_time = None
        hours_after_event = None
        
        if len(modified_first_breach) > 0:
            first_breach_idx = modified_first_breach.index[0]
            hours_after_event = first_breach_idx - event_mask.idxmax()
            first_breach_time = modified_event.loc[first_breach_idx, 'DateTime'].strftime('%Y-%m-%d %H:00')
        
        results[threshold_name] = {
            'threshold_temp': threshold_temp,
            'baseline_breach_ratio': float(avg_baseline),
            'modified_breach_ratio': float(avg_modified),
            'increase': float(avg_modified - avg_baseline),
            'first_breach_time': first_breach_time,
            'hours_after_event_start': int(hours_after_event) if hours_after_event is not None else None
        }
    
    return results


def generate_comfort_visualisations(
    baseline_df: pd.DataFrame,
    modified_df: pd.DataFrame,
    building_cols: List[str],
    building_labels: Dict[str, str],
    start_hour: int,
    output_dir: str,
    comfort_ranges: Optional[Dict] = None,
    event_name: str = "Event"
) -> Dict[str, str]:
    """
    Generate thermal comfort visualisation charts.
    
    Args:
        baseline_df: Baseline DataFrame
        modified_df: Modified DataFrame
        building_cols: List of building column names
        building_labels: Mapping of column names to building labels
        start_hour: Hour when the event starts
        output_dir: Directory to save output figures
        comfort_ranges: Optional custom comfort ranges
        event_name: Name of the event (e.g., "Heatwave", "Power Outage")
        
    Returns:
        Dictionary mapping figure names to file paths
    """
    if comfort_ranges is None:
        comfort_ranges = DEFAULT_COMFORT_RANGES
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    output_files = {}
    
    # Event period data
    event_mask = baseline_df['Hour'] >= start_hour
    baseline_event = baseline_df[event_mask].copy()
    modified_event = modified_df[event_mask].copy()
    
    event_date = baseline_event['DateTime'].iloc[0]
    
    # === Figure 1: Time Series Comparison ===
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # Subplot 1: Full year
    ax1 = axes[0]
    ax1.plot(baseline_df['DateTime'], baseline_df['Temp_Mean'], 
             label='Baseline', linewidth=1.5, alpha=0.8)
    ax1.plot(modified_df['DateTime'], modified_df['Temp_Mean'], 
             label='Modified', linewidth=1.5, alpha=0.8)
    ax1.axvline(event_date, color='red', linestyle='--', 
                linewidth=2, label=f'{event_name} start', alpha=0.7)
    ax1.axhspan(comfort_ranges['optimal'][0], comfort_ranges['optimal'][1], 
                alpha=0.1, color='green', label='Optimal comfort')
    ax1.axhspan(comfort_ranges['acceptable'][1], 100, 
                alpha=0.1, color='orange', label='Uncomfortable')
    ax1.axhspan(comfort_ranges['health_risk'][0], 100, 
                alpha=0.1, color='red', label='Health risk')
    ax1.set_ylabel('Average Indoor Temperature (°C)', fontsize=12)
    ax1.set_title(f'Annual Indoor Temperature Comparison (Average of {len(building_cols)} Buildings)', 
                  fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # Subplot 2: Event period
    ax2 = axes[1]
    ax2.plot(baseline_event['DateTime'], baseline_event['Temp_Mean'], 
             label='Baseline', linewidth=1.5, alpha=0.8)
    ax2.plot(modified_event['DateTime'], modified_event['Temp_Mean'], 
             label='Modified', linewidth=1.5, alpha=0.8)
    ax2.fill_between(baseline_event['DateTime'], 
                      baseline_event['Temp_Mean'], 
                      modified_event['Temp_Mean'],
                      where=(modified_event['Temp_Mean'] >= baseline_event['Temp_Mean']),
                      alpha=0.3, color='red', label='Temperature increase')
    ax2.axhline(comfort_ranges['optimal'][1], color='green', linestyle='--', 
                linewidth=1, label=f"Comfort limit ({comfort_ranges['optimal'][1]}°C)")
    ax2.axhline(comfort_ranges['acceptable'][1], color='orange', linestyle='--', 
                linewidth=1, label=f"Acceptable limit ({comfort_ranges['acceptable'][1]}°C)")
    ax2.axhline(comfort_ranges['slight_warm'][1], color='red', linestyle='--', 
                linewidth=1, label=f"Health risk ({comfort_ranges['slight_warm'][1]}°C)")
    ax2.set_ylabel('Average Indoor Temperature (°C)', fontsize=12)
    ax2.set_title(f'Detailed Temperature Comparison During {event_name}', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.tick_params(axis='both', which='major', labelsize=10)
    
    # Subplot 3: Temperature difference
    ax3 = axes[2]
    temp_diff = modified_event['Temp_Mean'] - baseline_event['Temp_Mean']
    ax3.fill_between(modified_event['DateTime'], 0, temp_diff,
                      where=(temp_diff >= 0), color='red', alpha=0.6, label='Increase')
    ax3.fill_between(modified_event['DateTime'], 0, temp_diff,
                      where=(temp_diff < 0), color='blue', alpha=0.6, label='Decrease')
    ax3.axhline(0, color='black', linewidth=1, linestyle='-')
    ax3.set_ylabel('Temperature Difference (°C)', fontsize=12)
    ax3.set_xlabel('Date', fontsize=12)
    ax3.set_title('Temperature Change (Modified - Baseline)', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax3.tick_params(axis='both', which='major', labelsize=10)
    
    plt.tight_layout()
    timeseries_file = output_path / 'thermal_comfort_timeseries.png'
    plt.savefig(timeseries_file, dpi=300, bbox_inches='tight')
    plt.close()
    output_files['timeseries'] = str(timeseries_file)
    
    # === Figure 2: Building-level Heatmap ===
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # Sample (one point per day)
    sample_freq = 24
    baseline_sample = baseline_event.iloc[::sample_freq][building_cols].T
    modified_sample = modified_event.iloc[::sample_freq][building_cols].T
    
    building_label_list = [building_labels[col] for col in building_cols]
    
    # Find first occurrence of each building type
    building_types = [label.split('_')[0] for label in building_label_list]
    type_first_positions = {}
    type_last_positions = {}
    ytick_positions = []
    ytick_labels = []
    
    for i, (building_type, label) in enumerate(zip(building_types, building_label_list)):
        if building_type not in type_first_positions:
            type_first_positions[building_type] = i
            ytick_positions.append(i)
            ytick_labels.append(building_type)
        type_last_positions[building_type] = i
    
    # Heatmap 1: Baseline
    im1 = axes[0].imshow(baseline_sample, aspect='auto', cmap='RdYlBu_r', 
                         vmin=15, vmax=40, interpolation='nearest')
    axes[0].set_ylabel('Building Type', fontsize=12)
    axes[0].set_title('Baseline: Daily Temperature Heatmap', fontsize=13, fontweight='bold')
    axes[0].set_yticks(ytick_positions)
    axes[0].set_yticklabels(ytick_labels, fontsize=10)
    axes[0].tick_params(axis='both', which='major', labelsize=10)
    
    for building_type, last_pos in type_last_positions.items():
        if last_pos < len(building_cols) - 1:
            axes[0].axhline(y=last_pos + 0.5, color='white', linewidth=1.5, alpha=0.7)
    
    cbar1 = plt.colorbar(im1, ax=axes[0], pad=0.01)
    cbar1.set_label('Temperature (°C)', fontsize=11)
    
    # Heatmap 2: Modified
    im2 = axes[1].imshow(modified_sample, aspect='auto', cmap='RdYlBu_r', 
                         vmin=15, vmax=40, interpolation='nearest')
    axes[1].set_ylabel('Building Type', fontsize=12)
    axes[1].set_xlabel(f'Days (Relative to {event_name} Start)', fontsize=12)
    axes[1].set_title('Modified: Daily Temperature Heatmap', fontsize=13, fontweight='bold')
    axes[1].set_yticks(ytick_positions)
    axes[1].set_yticklabels(ytick_labels, fontsize=10)
    axes[1].tick_params(axis='both', which='major', labelsize=10)
    
    for building_type, last_pos in type_last_positions.items():
        if last_pos < len(building_cols) - 1:
            axes[1].axhline(y=last_pos + 0.5, color='white', linewidth=1.5, alpha=0.7)
    
    cbar2 = plt.colorbar(im2, ax=axes[1], pad=0.01)
    cbar2.set_label('Temperature (°C)', fontsize=11)
    
    plt.tight_layout()
    heatmap_file = output_path / 'thermal_comfort_heatmap.png'
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    plt.close()
    output_files['heatmap'] = str(heatmap_file)
    
    return output_files


def generate_comfort_report(
    baseline_df: pd.DataFrame,
    modified_df: pd.DataFrame,
    building_cols: List[str],
    start_hour: int,
    threshold_results: Dict,
    output_file: str,
    event_name: str = "Event"
) -> Dict:
    """
    Generate thermal comfort analysis report.
    
    Args:
        baseline_df: Baseline DataFrame
        modified_df: Modified DataFrame
        building_cols: List of building column names
        start_hour: Hour when the event starts
        threshold_results: Results from threshold analysis
        output_file: Path to output report file
        event_name: Name of the event
        
    Returns:
        Dictionary with summary statistics
    """
    event_mask = baseline_df['Hour'] >= start_hour
    baseline_event = baseline_df[event_mask]
    modified_event = modified_df[event_mask]
    
    baseline_stats = {
        'mean': float(baseline_event['Temp_Mean'].mean()),
        'min': float(baseline_event['Temp_Mean'].min()),
        'max': float(baseline_event['Temp_Mean'].max()),
        'std': float(baseline_event['Temp_Mean'].std())
    }
    
    modified_stats = {
        'mean': float(modified_event['Temp_Mean'].mean()),
        'min': float(modified_event['Temp_Mean'].min()),
        'max': float(modified_event['Temp_Mean'].max()),
        'std': float(modified_event['Temp_Mean'].std())
    }
    
    # Generate text report
    report = []
    report.append("=" * 80)
    report.append(f"Thermal Comfort Impact Assessment Report - {event_name}")
    report.append("=" * 80)
    report.append("")
    report.append(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Number of buildings: {len(building_cols)}")
    report.append(f"Event period: {len(baseline_event)} hours")
    report.append("")
    report.append("-" * 80)
    report.append("1. Temperature Statistics")
    report.append("-" * 80)
    report.append(f"  Baseline:")
    report.append(f"    Average: {baseline_stats['mean']:.2f}°C")
    report.append(f"    Range: {baseline_stats['min']:.2f}°C - {baseline_stats['max']:.2f}°C")
    report.append(f"    Std Dev: {baseline_stats['std']:.2f}°C")
    report.append("")
    report.append(f"  Modified:")
    report.append(f"    Average: {modified_stats['mean']:.2f}°C")
    report.append(f"    Range: {modified_stats['min']:.2f}°C - {modified_stats['max']:.2f}°C")
    report.append(f"    Std Dev: {modified_stats['std']:.2f}°C")
    report.append("")
    report.append(f"  Changes:")
    report.append(f"    Average increase: {modified_stats['mean'] - baseline_stats['mean']:.2f}°C")
    report.append(f"    Peak increase: {modified_stats['max'] - baseline_stats['max']:.2f}°C")
    report.append("")
    report.append("-" * 80)
    report.append("2. Threshold Breach Analysis")
    report.append("-" * 80)
    
    for threshold_name, results in threshold_results.items():
        report.append(f"  {threshold_name} ({results['threshold_temp']}°C):")
        report.append(f"    Baseline breach: {results['baseline_breach_ratio']:.2f}%")
        report.append(f"    Modified breach: {results['modified_breach_ratio']:.2f}%")
        report.append(f"    Increase: {results['increase']:.2f} percentage points")
        if results['first_breach_time']:
            report.append(f"    First breach: {results['first_breach_time']}")
            report.append(f"    Time after event start: {results['hours_after_event_start']} hours")
        report.append("")
    
    report.append("=" * 80)
    report.append("End of Report")
    report.append("=" * 80)
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # Return summary
    summary = {
        'baseline_stats': baseline_stats,
        'modified_stats': modified_stats,
        'temperature_change': {
            'average': float(modified_stats['mean'] - baseline_stats['mean']),
            'peak': float(modified_stats['max'] - baseline_stats['max'])
        },
        'threshold_results': threshold_results,
        'report_file': output_file
    }
    
    return summary

