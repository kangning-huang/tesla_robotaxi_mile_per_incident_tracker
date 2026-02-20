#!/usr/bin/env python3
"""
Sync app.js interactive chart data with analysis_results.json and fleet_data.json.

This script updates the JavaScript data arrays in docs/app.js to match the latest
analysis results, ensuring the website's interactive charts stay in sync with
the backend calculations.

Run this after analyze_tesla_incidents.py to update the website data.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_incident_array(incidents: list, var_name: str = "incidentData") -> str:
    """Generate JavaScript incident data array string for chart visualization.

    Aggregates same-day incidents into monthly clusters.
    """
    if not incidents:
        return f"const {var_name} = [];"

    # Group by NHTSA date (original date before spreading)
    by_date = defaultdict(list)
    for inc in incidents:
        by_date[inc['incident_date']].append(inc)

    # For each unique date, create one data point
    lines = []
    for date_str in sorted(by_date.keys()):
        date_incidents = by_date[date_str]
        incident_count = len(date_incidents)

        # Sum all miles for this cluster and calculate cluster MPI
        total_miles = sum(int(inc['miles_since_previous']) for inc in date_incidents)
        cluster_mpi = total_miles // incident_count if incident_count > 0 else 0

        # Use known date if available, otherwise use mid-month for visibility
        month_key = date_str[:7]
        known_dates = {
            '2025-07': '2025-07-15',
            '2025-09': '2025-09-15',
            '2025-10': '2025-10-15',
            '2025-11': '2025-11-12',
            '2025-12': '2025-12-10',
            '2026-01': '2026-01-10',
            '2026-02': '2026-02-10',
        }
        viz_date = known_dates.get(month_key, date_str)

        avg_fleet = sum(inc['avg_fleet_size'] for inc in date_incidents) / incident_count
        days = date_incidents[0]['days_since_previous']

        # Include incident count for tooltip
        lines.append(f"    {{ date: '{viz_date}', days: {days}, fleet: {int(avg_fleet)}, miles: {total_miles}, mpi: {cluster_mpi}, count: {incident_count} }},")

    return f"const {var_name} = [\n" + "\n".join(lines) + "\n];"


def filter_incidents(incidents: list, exclude_backing: bool = True, exclude_stationary: bool = True) -> list:
    """Filter incidents based on type using NHTSA data fields.

    Backing incidents: Low-speed reversing events in parking lots
      (Roadway Type == "Parking Lot" and SV Pre-Crash Movement == "Backing")
    Stationary incidents: 0 mph incidents where the robotaxi was stopped
      (SV Precrash Speed == 0 and SV Pre-Crash Movement == "Stopped")
    """
    filtered = []
    for inc in incidents:
        precrash_speed = inc.get('precrash_speed_mph')
        precrash_movement = inc.get('precrash_movement', '')
        roadway_type = inc.get('roadway_type', '')

        is_backing = (roadway_type == 'Parking Lot' and precrash_movement == 'Backing')
        is_stationary = (precrash_speed == 0 and precrash_movement == 'Stopped')

        if exclude_backing and is_backing:
            continue
        if exclude_stationary and is_stationary:
            continue

        filtered.append(inc)

    return filtered


def recalculate_mpi(incidents: list, daily_miles: int = 115) -> list:
    """Recalculate MPI values after filtering.

    When incidents are removed, the miles between remaining incidents change.
    """
    if not incidents:
        return []

    result = []
    prev_date = None
    cumulative_miles = 0

    for i, inc in enumerate(incidents):
        new_inc = inc.copy()

        if i == 0:
            # First incident - use original values
            result.append(new_inc)
            prev_date = datetime.strptime(inc['incident_date'], '%Y-%m-%d')
            cumulative_miles = inc['cumulative_miles']
        else:
            current_date = datetime.strptime(inc['incident_date'], '%Y-%m-%d')
            days = (current_date - prev_date).days

            # Recalculate miles based on fleet size and days
            # This is a simplified calculation - ideally we'd use actual fleet data
            miles = int(inc['avg_fleet_size']) * daily_miles * max(days, 1)

            new_inc['days_since_previous'] = days
            new_inc['miles_since_previous'] = miles
            new_inc['mpi_since_previous'] = miles  # Single incident interval
            cumulative_miles += miles
            new_inc['cumulative_miles'] = cumulative_miles
            new_inc['cumulative_incidents'] = i + 1
            new_inc['cumulative_mpi'] = cumulative_miles / (i + 1)

            result.append(new_inc)
            prev_date = current_date

    return result


def generate_fleet_data(snapshots: list) -> str:
    """Generate JavaScript fleetData array string."""
    lines = []
    for snapshot in snapshots:
        date = snapshot['date']
        size = snapshot.get('austin_vehicles')
        if size:
            lines.append(f"    {{ date: '{date}', size: {size} }},")
    return "const fleetData = [\n" + "\n".join(lines) + "\n];"


def get_latest_active_fleet(snapshots: list) -> int:
    """Get the latest active fleet size."""
    active_sizes = [s.get('austin_active_vehicles') for s in snapshots if s.get('austin_active_vehicles')]
    return active_sizes[-1] if active_sizes else 46


def generate_all_filter_combinations(analysis: dict) -> dict:
    """Generate incident data for all filter combinations.

    Returns a dict with keys for each combination:
    - base: no backing, no stationary (most filtered, DEFAULT)
    - stationary: no backing, WITH stationary
    - backing: WITH backing, no stationary
    - all: WITH backing, WITH stationary (least filtered)
    """
    total_incidents = analysis['incidents']
    active_incidents = analysis['active_fleet']['incidents']

    combinations = {}

    # Generate combinations for total fleet
    combinations['total_base'] = recalculate_mpi(
        filter_incidents(total_incidents, exclude_backing=True, exclude_stationary=True)
    )
    combinations['total_stationary'] = recalculate_mpi(
        filter_incidents(total_incidents, exclude_backing=True, exclude_stationary=False)
    )
    combinations['total_backing'] = recalculate_mpi(
        filter_incidents(total_incidents, exclude_backing=False, exclude_stationary=True)
    )
    combinations['total_all'] = recalculate_mpi(
        filter_incidents(total_incidents, exclude_backing=False, exclude_stationary=False)
    )

    # Generate combinations for active fleet
    combinations['active_base'] = recalculate_mpi(
        filter_incidents(active_incidents, exclude_backing=True, exclude_stationary=True)
    )
    combinations['active_stationary'] = recalculate_mpi(
        filter_incidents(active_incidents, exclude_backing=True, exclude_stationary=False)
    )
    combinations['active_backing'] = recalculate_mpi(
        filter_incidents(active_incidents, exclude_backing=False, exclude_stationary=True)
    )
    combinations['active_all'] = recalculate_mpi(
        filter_incidents(active_incidents, exclude_backing=False, exclude_stationary=False)
    )

    return combinations


def update_app_js(app_js_path: Path, analysis: dict, fleet: dict) -> bool:
    """
    Update app.js with new data from analysis results and fleet data.

    Generates all filter combinations for incident data.

    Returns True if changes were made, False otherwise.
    """
    with open(app_js_path, 'r') as f:
        original_content = f.read()

    content = original_content

    # Generate all filter combinations
    combinations = generate_all_filter_combinations(analysis)

    # Generate JavaScript arrays for each combination
    # Total fleet
    base_str = generate_incident_array(combinations['total_base'], 'incidentDataBase')
    stationary_str = generate_incident_array(combinations['total_stationary'], 'incidentDataStationary')
    backing_str = generate_incident_array(combinations['total_backing'], 'incidentDataBacking')
    all_str = generate_incident_array(combinations['total_all'], 'incidentDataAll')

    # Active fleet
    active_base_str = generate_incident_array(combinations['active_base'], 'incidentDataActiveBase')
    active_stationary_str = generate_incident_array(combinations['active_stationary'], 'incidentDataActiveStationary')
    active_backing_str = generate_incident_array(combinations['active_backing'], 'incidentDataActiveBacking')
    active_all_str = generate_incident_array(combinations['active_all'], 'incidentDataActiveAll')

    fleet_data_str = generate_fleet_data(fleet['snapshots'])
    latest_active = get_latest_active_fleet(fleet['snapshots'])

    # Replace each data array
    replacements = [
        (r'const incidentDataBase = \[[\s\S]*?\];', base_str),
        (r'const incidentDataStationary = \[[\s\S]*?\];', stationary_str),
        (r'const incidentDataBacking = \[[\s\S]*?\];', backing_str),
        (r'const incidentDataAll = \[[\s\S]*?\];', all_str),
        (r'const incidentDataActiveBase = \[[\s\S]*?\];', active_base_str),
        (r'const incidentDataActiveStationary = \[[\s\S]*?\];', active_stationary_str),
        (r'const incidentDataActiveBacking = \[[\s\S]*?\];', active_backing_str),
        (r'const incidentDataActiveAll = \[[\s\S]*?\];', active_all_str),
        (r'const latestActiveFleetSize = \d+;', f'const latestActiveFleetSize = {latest_active};'),
        (r'const fleetData = \[[\s\S]*?\];', fleet_data_str),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, count=1)

    # Check if anything changed
    if content == original_content:
        return False

    # Write back
    with open(app_js_path, 'w') as f:
        f.write(content)

    return True


def main():
    """Main entry point."""
    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    data_dir = repo_root / "data"
    docs_dir = repo_root / "docs"

    analysis_path = data_dir / "analysis_results.json"
    fleet_path = data_dir / "fleet_data.json"
    app_js_path = docs_dir / "app.js"

    print("=" * 60)
    print("SYNC APP.JS WITH ANALYSIS DATA")
    print("=" * 60)

    # Check files exist
    for path, name in [(analysis_path, "analysis_results.json"),
                       (fleet_path, "fleet_data.json"),
                       (app_js_path, "app.js")]:
        if not path.exists():
            print(f"Error: {name} not found at {path}")
            return 1

    # Load data
    print(f"\nLoading {analysis_path.name}...")
    analysis = load_json(analysis_path)
    print(f"  Incidents: {len(analysis['incidents'])}")

    print(f"\nLoading {fleet_path.name}...")
    fleet = load_json(fleet_path)
    print(f"  Fleet snapshots: {len(fleet['snapshots'])}")

    # Get stats
    latest_fleet = fleet['snapshots'][-1]
    latest_active = get_latest_active_fleet(fleet['snapshots'])

    # Generate combinations for reporting
    combinations = generate_all_filter_combinations(analysis)

    print(f"\nFilter combinations generated:")
    print(f"  Base (no backing, no stationary): {len(combinations['total_base'])} incidents")
    print(f"  Stationary (no backing, with stationary): {len(combinations['total_stationary'])} incidents")
    print(f"  Backing (with backing, no stationary): {len(combinations['total_backing'])} incidents")
    print(f"  All (with backing, with stationary): {len(combinations['total_all'])} incidents")

    print(f"\nLatest data:")
    print(f"  Fleet size: {latest_fleet.get('austin_vehicles', 'N/A')} vehicles")
    print(f"  Active fleet: {latest_active} vehicles")
    print(f"  Last incident: {analysis['incidents'][-1]['incident_date']}")

    # Update app.js
    print(f"\nUpdating {app_js_path.name}...")
    changed = update_app_js(app_js_path, analysis, fleet)

    if changed:
        print("  ✓ app.js updated successfully")
        print(f"\nSync complete:")
        print(f"  - 8 incident data arrays generated (4 total fleet, 4 active fleet)")
        print(f"  - {len([s for s in fleet['snapshots'] if s.get('austin_vehicles')])} fleet data points")
        return 0
    else:
        print("  ○ No changes needed (app.js already up to date)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
