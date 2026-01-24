#!/usr/bin/env python3
"""
Analyze Tesla Robotaxi incidents from NHTSA data and calculate miles-per-incident.

This script:
1. Loads NHTSA ADS/ADAS CSV data
2. Filters for Tesla incidents
3. Combines with fleet size data
4. Calculates estimated miles per incident
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas")
    sys.exit(1)


def load_nhtsa_data(data_dir: Path) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Load NHTSA ADS and ADAS CSV files."""
    ads_file = data_dir / "SGO-2021-01_Incident_Reports_ADS.csv"
    adas_file = data_dir / "SGO-2021-01_Incident_Reports_ADAS.csv"

    ads_df = None
    adas_df = None

    if ads_file.exists():
        print(f"Loading ADS data from {ads_file}")
        ads_df = pd.read_csv(ads_file, low_memory=False)
        print(f"  Loaded {len(ads_df)} ADS incidents")
    else:
        print(f"Warning: ADS file not found: {ads_file}")

    if adas_file.exists():
        print(f"Loading ADAS data from {adas_file}")
        adas_df = pd.read_csv(adas_file, low_memory=False)
        print(f"  Loaded {len(adas_df)} ADAS incidents")
    else:
        print(f"Warning: ADAS file not found: {adas_file}")

    return ads_df, adas_df


def filter_tesla_incidents(df: pd.DataFrame, system_type: str) -> pd.DataFrame:
    """Filter dataframe for Tesla incidents only."""
    if df is None:
        return pd.DataFrame()

    # Common column names for manufacturer/make
    make_columns = ['Make', 'MAKE', 'Manufacturer', 'MANUFACTURER', 'Vehicle Make']

    make_col = None
    for col in make_columns:
        if col in df.columns:
            make_col = col
            break

    if make_col is None:
        print(f"  Warning: Could not find make column. Available: {list(df.columns)[:10]}...")
        return pd.DataFrame()

    # Filter for Tesla
    tesla_df = df[df[make_col].str.contains('Tesla', case=False, na=False)].copy()
    tesla_df['System_Type'] = system_type

    print(f"  Found {len(tesla_df)} Tesla {system_type} incidents")
    return tesla_df


def load_fleet_data(data_dir: Path) -> list[dict]:
    """Load fleet size snapshots from JSON."""
    fleet_file = data_dir / "fleet_data.json"

    if not fleet_file.exists():
        print(f"Warning: Fleet data not found: {fleet_file}")
        return []

    with open(fleet_file) as f:
        data = json.load(f)

    return data.get("snapshots", [])


def interpolate_fleet_size(fleet_snapshots: list[dict], target_date: datetime) -> int:
    """Estimate fleet size at a given date by interpolation."""
    if not fleet_snapshots:
        return 25  # Default estimate

    # Convert to datetime and sort
    snapshots = []
    for s in fleet_snapshots:
        dt = datetime.strptime(s["date"], "%Y-%m-%d")
        snapshots.append((dt, s.get("total_robotaxi", s.get("austin_vehicles", 0))))

    snapshots.sort(key=lambda x: x[0])

    # Find surrounding snapshots
    before = None
    after = None

    for dt, count in snapshots:
        if dt <= target_date:
            before = (dt, count)
        if dt >= target_date and after is None:
            after = (dt, count)

    # Interpolate
    if before is None:
        return snapshots[0][1] if snapshots else 25
    if after is None:
        return before[1]
    if before[0] == after[0]:
        return before[1]

    # Linear interpolation
    total_days = (after[0] - before[0]).days
    elapsed_days = (target_date - before[0]).days
    ratio = elapsed_days / total_days if total_days > 0 else 0

    return int(before[1] + (after[1] - before[1]) * ratio)


def calculate_miles_per_incident(
    incidents_df: pd.DataFrame,
    fleet_snapshots: list[dict],
    daily_miles: int = 100,
    start_date: str = "2025-06-25",
    end_date: str = None
) -> dict:
    """Calculate miles per incident metric."""

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()

    # Count incidents in period
    if incidents_df is not None and len(incidents_df) > 0:
        # Try to find date column
        date_columns = ['Incident Date', 'Date', 'INCIDENT_DATE', 'Report Date']
        date_col = None
        for col in date_columns:
            if col in incidents_df.columns:
                date_col = col
                break

        if date_col:
            incidents_df['_parsed_date'] = pd.to_datetime(incidents_df[date_col], errors='coerce')
            period_incidents = incidents_df[
                (incidents_df['_parsed_date'] >= start_dt) &
                (incidents_df['_parsed_date'] <= end_dt)
            ]
            incident_count = len(period_incidents)
        else:
            incident_count = len(incidents_df)
    else:
        incident_count = 0

    # Calculate total miles
    total_days = (end_dt - start_dt).days
    total_miles = 0

    # Sum miles for each day based on fleet size
    current_date = start_dt
    while current_date <= end_dt:
        fleet_size = interpolate_fleet_size(fleet_snapshots, current_date)
        total_miles += fleet_size * daily_miles
        current_date += timedelta(days=1)

    # Calculate metric
    miles_per_incident = total_miles / incident_count if incident_count > 0 else float('inf')

    return {
        "period_start": start_date,
        "period_end": end_dt.strftime("%Y-%m-%d"),
        "total_days": total_days,
        "incident_count": incident_count,
        "daily_miles_assumption": daily_miles,
        "estimated_total_miles": total_miles,
        "miles_per_incident": miles_per_incident
    }


def print_report(results: dict, scenario_name: str):
    """Print formatted report for a scenario."""
    print(f"\n  {scenario_name} ({results['daily_miles_assumption']} mi/day/vehicle):")
    print(f"    Total estimated miles: {results['estimated_total_miles']:,.0f}")
    print(f"    Miles per incident: {results['miles_per_incident']:,.0f}")


def main():
    """Main analysis function."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    print("=" * 70)
    print("TESLA ROBOTAXI MILES PER INCIDENT ANALYSIS")
    print("=" * 70)
    print(f"\nData directory: {data_dir}")
    print(f"Analysis date: {datetime.now().isoformat()}")

    # Load data
    print("\n" + "=" * 70)
    print("LOADING DATA")
    print("=" * 70)

    ads_df, adas_df = load_nhtsa_data(data_dir)
    fleet_snapshots = load_fleet_data(data_dir)

    # Filter for Tesla
    print("\n" + "=" * 70)
    print("FILTERING TESLA INCIDENTS")
    print("=" * 70)

    tesla_ads = filter_tesla_incidents(ads_df, "ADS")
    tesla_adas = filter_tesla_incidents(adas_df, "ADAS")

    # Combine Tesla incidents
    all_tesla = pd.concat([tesla_ads, tesla_adas], ignore_index=True) if len(tesla_ads) > 0 or len(tesla_adas) > 0 else pd.DataFrame()

    print(f"\nTotal Tesla incidents found: {len(all_tesla)}")

    if len(all_tesla) == 0:
        print("\n⚠ No Tesla incidents found in data.")
        print("Please run: python scripts/download_nhtsa_data.py first")

        # Use sample data for demonstration
        print("\n" + "=" * 70)
        print("USING SAMPLE DATA FOR DEMONSTRATION")
        print("=" * 70)
        sample_incident_count = 8  # Known incidents through Oct 2025
        print(f"Known Tesla Robotaxi incidents (from news): {sample_incident_count}")
    else:
        sample_incident_count = None

    # Calculate metrics
    print("\n" + "=" * 70)
    print("MILES PER INCIDENT CALCULATION")
    print("=" * 70)

    period_start = "2025-06-25"
    period_end = "2025-12-15"

    print(f"\nPeriod: {period_start} to {period_end}")
    print(f"Fleet snapshots available: {len(fleet_snapshots)}")

    # Calculate for different scenarios
    scenarios = [
        ("Conservative", 50),
        ("Moderate", 100),
        ("Aggressive", 150)
    ]

    if sample_incident_count:
        # Create a dummy dataframe with known count
        dummy_df = pd.DataFrame({'date': [period_start] * sample_incident_count})
        calc_df = dummy_df
    else:
        calc_df = all_tesla

    for scenario_name, daily_miles in scenarios:
        results = calculate_miles_per_incident(
            calc_df,
            fleet_snapshots,
            daily_miles=daily_miles,
            start_date=period_start,
            end_date=period_end
        )
        print_report(results, scenario_name)

    # Comparison benchmarks
    print("\n" + "=" * 70)
    print("COMPARISON BENCHMARKS")
    print("=" * 70)
    print("\n  Human Drivers (US avg):     ~500,000 miles per accident")
    print("  Waymo (reported):           ~1,000,000+ miles per incident")
    print("  Tesla FSD (supervised):     ~3,400,000 miles per crash (Tesla claim)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    incident_count = sample_incident_count if sample_incident_count else len(all_tesla)

    if incident_count > 0:
        moderate_results = calculate_miles_per_incident(
            calc_df, fleet_snapshots, daily_miles=100,
            start_date=period_start, end_date=period_end
        )
        mpi = moderate_results['miles_per_incident']

        print(f"\n  Tesla Robotaxi (estimated, moderate): ~{mpi:,.0f} miles per incident")

        # Safety ratio vs human drivers
        human_mpi = 500000
        ratio = human_mpi / mpi if mpi > 0 else 0
        print(f"  Ratio vs human drivers: {ratio:.1f}x {'worse' if ratio > 1 else 'better'}")
    else:
        print("\n  Insufficient data for calculation")

    print("\n" + "=" * 70)
    print("NOTES")
    print("=" * 70)
    print("""
  - Miles per incident is ESTIMATED based on fleet size and assumed daily miles
  - Tesla does not publish official miles driven data
  - NHTSA data may have reporting delays (Tesla cited for late reporting)
  - Not all incidents are equal in severity
  - Austin robotaxis have passenger monitors; not fully unsupervised
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
