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
    """
    # Group incidents by date
    by_date = defaultdict(list)
    for i, inc in enumerate(incidents):
        by_date[inc['incident_date']].append((i, inc))

    # Create new list with spread dates
    result = []
    for date_str, date_incidents in by_date.items():
        if len(date_incidents) == 1:
            # Single incident on this date - keep as is
            result.append((date_incidents[0][0], date_incidents[0][1], date_str))
        else:
            # Multiple incidents on same date - spread across month
            try:
                base_date = datetime.strptime(date_str, '%Y-%m-%d')
                # Spread incidents across ~25 days of the month
                spacing = 25 // len(date_incidents)
                for j, (idx, inc) in enumerate(date_incidents):
                    new_date = base_date + timedelta(days=j * spacing)
                    result.append((idx, inc, new_date.strftime('%Y-%m-%d')))
            except ValueError:
                # If date parsing fails, keep original
                for idx, inc in date_incidents:
                    result.append((idx, inc, date_str))

    # Sort by original index to maintain order
    result.sort(key=lambda x: x[0])
    return [(inc, viz_date) for _, inc, viz_date in result]


def generate_incident_data(incidents: list) -> str:
    """Generate JavaScript incidentData array string with spread dates for visualization."""
    # Spread same-day incidents for better chart display
    spread_incidents = spread_same_day_incidents(incidents)

    lines = []
    for inc, viz_date in spread_incidents:
        days = inc['days_since_previous']
        fleet_size = int(inc['avg_fleet_size'])
        miles = int(inc['miles_since_previous'])
        mpi = int(inc['mpi_since_previous'])
        lines.append(f"    {{ date: '{viz_date}', days: {days}, fleet: {fleet_size}, miles: {miles}, mpi: {mpi} }},")
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
