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


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_incident_data(incidents: list) -> str:
    """Generate JavaScript incidentData array string."""
    lines = []
    for inc in incidents:
        date = inc['incident_date']
        days = inc['days_since_previous']
        fleet_size = int(inc['avg_fleet_size'])
        miles = int(inc['miles_since_previous'])
        mpi = int(inc['mpi_since_previous'])
        lines.append(f"    {{ date: '{date}', days: {days}, fleet: {fleet_size}, miles: {miles}, mpi: {mpi} }},")
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
