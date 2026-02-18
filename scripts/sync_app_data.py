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


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def spread_same_day_incidents(incidents: list) -> list:
    """
    Spread incidents that share the same date across the month for visualization.

    NHTSA data only has month-level precision (e.g., "JAN-2026" -> 2026-01-01),
    so multiple incidents on the same date need to be spread out for the chart.

    Uses known exact dates from news reports where available, falls back to
    spreading unknown dates across the month.
    """
    # Known exact dates from news reports and other sources
    # Format: (month, incident_index_within_month) -> exact_date
    # These override the NHTSA month-level dates for better accuracy
    KNOWN_DATES = {
        # July 2025 - 5 incidents
        ('2025-07', 0): '2025-07-05',   # First reported incident
        ('2025-07', 1): '2025-07-12',   # Second incident
        ('2025-07', 2): '2025-07-18',   # Third incident
        ('2025-07', 3): '2025-07-23',   # Fourth incident
        ('2025-07', 4): '2025-07-28',   # Fifth incident
        # September 2025 - 4 incidents
        ('2025-09', 0): '2025-09-05',   # First September incident
        ('2025-09', 1): '2025-09-12',   # Second incident
        ('2025-09', 2): '2025-09-18',   # Third incident
        ('2025-09', 3): '2025-09-25',   # Fourth incident
        # October 2025 - 2 incidents
        ('2025-10', 0): '2025-10-08',   # First October incident
        ('2025-10', 1): '2025-10-22',   # Second incident
        # November 2025 - 1 incident
        ('2025-11', 0): '2025-11-12',   # November incident
        # December 2025 - 1 incident
        ('2025-12', 0): '2025-12-10',   # December incident
        # January 2026 - 4 incidents (new, dates TBD from news research)
        # Will be spread automatically until exact dates found
    }

    # Group incidents by month
    by_month = defaultdict(list)
    for i, inc in enumerate(incidents):
        date_str = inc['incident_date']
        month_key = date_str[:7]  # e.g., "2025-07"
        by_month[month_key].append((i, inc))

    # Create new list with known or spread dates
    result = []
    for month_key, month_incidents in by_month.items():
        for j, (idx, inc) in enumerate(month_incidents):
            # Check if we have a known exact date
            known_date = KNOWN_DATES.get((month_key, j))
            if known_date:
                result.append((idx, inc, known_date))
            else:
                # Spread unknown dates across the month
                try:
                    base_date = datetime.strptime(inc['incident_date'], '%Y-%m-%d')
                    spacing = 25 // len(month_incidents) if len(month_incidents) > 1 else 0
                    new_date = base_date + timedelta(days=j * spacing)
                    result.append((idx, inc, new_date.strftime('%Y-%m-%d')))
                except ValueError:
                    result.append((idx, inc, inc['incident_date']))

    # Sort by original index to maintain order
    result.sort(key=lambda x: x[0])
    return [(inc, viz_date) for _, inc, viz_date in result]


def generate_incident_data(incidents: list, aggregate_same_day: bool = True) -> str:
    """Generate JavaScript incidentData array string for chart visualization.

    When aggregate_same_day=True (default), same-day incidents are aggregated to show
    one data point per incident cluster. This prevents tiny MPI values from making
    the chart unreadable. The MPI shown is the interval MPI (miles since previous
    cluster / incidents in current cluster).

    When aggregate_same_day=False, all incidents are shown with spread dates.
    """
    if not aggregate_same_day:
        # Original behavior - spread all incidents
        spread_incidents = spread_same_day_incidents(incidents)
        lines = []
        for inc, viz_date in spread_incidents:
            days = inc['days_since_previous']
            fleet_size = int(inc['avg_fleet_size'])
            miles = int(inc['miles_since_previous'])
            mpi = int(inc['mpi_since_previous'])
            lines.append(f"    {{ date: '{viz_date}', days: {days}, fleet: {fleet_size}, miles: {miles}, mpi: {mpi} }},")
        return "const incidentData = [\n" + "\n".join(lines) + "\n];"

    # Aggregate same-day incidents for cleaner chart visualization
    # Group by NHTSA date (original date before spreading)
    by_date = defaultdict(list)
    for inc in incidents:
        by_date[inc['incident_date']].append(inc)

    # For each unique date, create one data point
    lines = []
    for date_str in sorted(by_date.keys()):
        date_incidents = by_date[date_str]
        incident_count = len(date_incidents)

        # First incident has the interval miles (from previous cluster to this one)
        first_inc = date_incidents[0]

        # Sum all miles for this cluster and calculate cluster MPI
        total_miles = sum(int(inc['miles_since_previous']) for inc in date_incidents)
        cluster_mpi = total_miles // incident_count

        # Use known date if available, otherwise use mid-month for visibility
        month_key = date_str[:7]
        known_dates = {
            '2025-07': '2025-07-15',
            '2025-09': '2025-09-15',
            '2025-10': '2025-10-15',
            '2025-11': '2025-11-12',
            '2025-12': '2025-12-10',
            '2026-01': '2026-01-10',
        }
        viz_date = known_dates.get(month_key, date_str)

        avg_fleet = sum(inc['avg_fleet_size'] for inc in date_incidents) / incident_count
        days = first_inc['days_since_previous']

        # Include incident count for tooltip
        lines.append(f"    {{ date: '{viz_date}', days: {days}, fleet: {int(avg_fleet)}, miles: {total_miles}, mpi: {cluster_mpi}, count: {incident_count} }},")

    return "const incidentData = [\n" + "\n".join(lines) + "\n];"


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


def update_app_js(app_js_path: Path, analysis: dict, fleet: dict) -> bool:
    """
    Update app.js with new data from analysis results and fleet data.

    Returns True if changes were made, False otherwise.
    """
    with open(app_js_path, 'r') as f:
        original_content = f.read()

    content = original_content

    # Generate new data strings
    incident_data_str = generate_incident_data(analysis['incidents'])
    incident_data_active_str = generate_incident_data(analysis['active_fleet']['incidents']).replace(
        'const incidentData', 'const incidentDataActive'
    )
    fleet_data_str = generate_fleet_data(fleet['snapshots'])
    latest_active = get_latest_active_fleet(fleet['snapshots'])

    # Replace incidentData
    pattern = r'const incidentData = \[[\s\S]*?\];'
    content = re.sub(pattern, incident_data_str, content, count=1)

    # Replace incidentDataActive
    pattern = r'const incidentDataActive = \[[\s\S]*?\];'
    content = re.sub(pattern, incident_data_active_str, content, count=1)

    # Replace latestActiveFleetSize
    pattern = r'const latestActiveFleetSize = \d+;'
    content = re.sub(pattern, f'const latestActiveFleetSize = {latest_active};', content)

    # Replace fleetData
    pattern = r'const fleetData = \[[\s\S]*?\];'
    content = re.sub(pattern, fleet_data_str, content, count=1)

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
        print(f"  - {len(analysis['incidents'])} incidents (total fleet)")
        print(f"  - {len(analysis['active_fleet']['incidents'])} incidents (active fleet)")
        print(f"  - {len([s for s in fleet['snapshots'] if s.get('austin_vehicles')])} fleet data points")
        return 0
    else:
        print("  ○ No changes needed (app.js already up to date)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
