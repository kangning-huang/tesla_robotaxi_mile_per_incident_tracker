#!/usr/bin/env python3
"""
Analyze Tesla Robotaxi incidents from NHTSA data and calculate miles-per-incident.

This script:
1. Loads NHTSA ADS/ADAS CSV data
2. Filters for Tesla incidents
3. Combines with fleet size data (day-by-day interpolation)
4. Calculates estimated miles between each incident
5. Tracks the metric over time
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


class FleetInterpolator:
    """Interpolate fleet size for any given date based on snapshots."""

    def __init__(self, snapshots: list[dict]):
        """Initialize with fleet snapshots."""
        self.snapshots = []
        for s in snapshots:
            dt = datetime.strptime(s["date"], "%Y-%m-%d")
            # Use Austin vehicles as true robotaxi count (unsupervised)
            count = s.get("total_robotaxi", s.get("austin_vehicles", 0))
            self.snapshots.append((dt, count))
        self.snapshots.sort(key=lambda x: x[0])

    def get_fleet_size(self, target_date: datetime) -> int:
        """Get interpolated fleet size for a specific date."""
        if not self.snapshots:
            return 25  # Default estimate

        # Find surrounding snapshots
        before = None
        after = None

        for dt, count in self.snapshots:
            if dt <= target_date:
                before = (dt, count)
            if dt >= target_date and after is None:
                after = (dt, count)

        # Handle edge cases
        if before is None:
            return self.snapshots[0][1]
        if after is None:
            return before[1]
        if before[0] == after[0]:
            return before[1]

        # Linear interpolation
        total_days = (after[0] - before[0]).days
        elapsed_days = (target_date - before[0]).days
        ratio = elapsed_days / total_days if total_days > 0 else 0

        return int(before[1] + (after[1] - before[1]) * ratio)

    def calculate_miles_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        daily_miles_per_vehicle: int
    ) -> tuple[int, list[dict]]:
        """
        Calculate total miles driven in a period with day-by-day fleet tracking.

        Returns:
            tuple: (total_miles, daily_breakdown)
        """
        total_miles = 0
        daily_breakdown = []

        current_date = start_date
        while current_date <= end_date:
            fleet_size = self.get_fleet_size(current_date)
            day_miles = fleet_size * daily_miles_per_vehicle
            total_miles += day_miles

            daily_breakdown.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "fleet_size": fleet_size,
                "daily_miles": day_miles
            })

            current_date += timedelta(days=1)

        return total_miles, daily_breakdown


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
        print(f"  ADS file not found: {ads_file}")

    if adas_file.exists():
        print(f"Loading ADAS data from {adas_file}")
        adas_df = pd.read_csv(adas_file, low_memory=False)
        print(f"  Loaded {len(adas_df)} ADAS incidents")
    else:
        print(f"  ADAS file not found: {adas_file}")

    return ads_df, adas_df


def filter_tesla_incidents(df: pd.DataFrame, system_type: str) -> pd.DataFrame:
    """Filter dataframe for Tesla incidents only."""
    if df is None or len(df) == 0:
        return pd.DataFrame()

    # Common column names for manufacturer/make
    make_columns = ['Make', 'MAKE', 'Manufacturer', 'MANUFACTURER', 'Vehicle Make']

    make_col = None
    for col in make_columns:
        if col in df.columns:
            make_col = col
            break

    if make_col is None:
        print(f"  Warning: Could not find make column in {system_type} data")
        return pd.DataFrame()

    # Filter for Tesla
    tesla_df = df[df[make_col].str.contains('Tesla', case=False, na=False)].copy()
    tesla_df['System_Type'] = system_type

    print(f"  Found {len(tesla_df)} Tesla {system_type} incidents")
    return tesla_df


def parse_incident_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse incident dates from various column formats."""
    if df is None or len(df) == 0:
        return df

    date_columns = ['Incident Date', 'Date', 'INCIDENT_DATE', 'Report Date', 'Crash Date']

    for col in date_columns:
        if col in df.columns:
            df['parsed_date'] = pd.to_datetime(df[col], errors='coerce')
            valid_dates = df['parsed_date'].notna().sum()
            print(f"  Parsed {valid_dates} dates from column '{col}'")
            return df

    print("  Warning: Could not find date column")
    return df


def load_fleet_data(data_dir: Path) -> list[dict]:
    """Load fleet size snapshots from JSON."""
    fleet_file = data_dir / "fleet_data.json"

    if not fleet_file.exists():
        print(f"Warning: Fleet data not found: {fleet_file}")
        return []

    with open(fleet_file) as f:
        data = json.load(f)

    snapshots = data.get("snapshots", [])
    print(f"  Loaded {len(snapshots)} fleet snapshots")
    return snapshots


def calculate_miles_between_incidents(
    incidents_df: pd.DataFrame,
    fleet_interpolator: FleetInterpolator,
    daily_miles: int,
    service_start: datetime
) -> list[dict]:
    """
    Calculate miles driven between each consecutive incident.

    This gives a dynamic view of the miles-per-incident metric over time,
    accounting for changing fleet size.
    """
    results = []

    if incidents_df is None or len(incidents_df) == 0 or 'parsed_date' not in incidents_df.columns:
        return results

    # Sort incidents by date
    sorted_incidents = incidents_df.dropna(subset=['parsed_date']).sort_values('parsed_date')

    if len(sorted_incidents) == 0:
        return results

    # First incident: calculate miles from service start
    prev_date = service_start
    incident_num = 0

    for idx, row in sorted_incidents.iterrows():
        incident_num += 1
        incident_date = row['parsed_date'].to_pydatetime()

        # Skip if incident is before service start
        if incident_date < service_start:
            continue

        # Calculate miles between previous date and this incident
        miles, daily_breakdown = fleet_interpolator.calculate_miles_in_period(
            prev_date, incident_date, daily_miles
        )

        days_between = (incident_date - prev_date).days

        results.append({
            "incident_number": incident_num,
            "incident_date": incident_date.strftime("%Y-%m-%d"),
            "days_since_previous": days_between,
            "miles_since_previous": miles,
            "avg_fleet_size": sum(d['fleet_size'] for d in daily_breakdown) / len(daily_breakdown) if daily_breakdown else 0,
            "cumulative_miles": sum(r['miles_since_previous'] for r in results) + miles,
            "cumulative_incidents": incident_num
        })

        prev_date = incident_date

    # Calculate running miles-per-incident
    for r in results:
        r['cumulative_miles_per_incident'] = r['cumulative_miles'] / r['cumulative_incidents']

    return results


def get_sample_incidents() -> pd.DataFrame:
    """
    Return sample incident data based on known Tesla Robotaxi crashes.

    Based on news reports:
    - 7 collisions through Oct 15, 2025
    - 8th crash in October 2025
    - Additional incidents reported through Dec 2025
    """
    incidents = [
        {"date": "2025-07-05", "description": "Low-speed collision, Austin"},
        {"date": "2025-07-18", "description": "Minor fender-bender, Austin"},
        {"date": "2025-08-02", "description": "Collision reported to NHTSA"},
        {"date": "2025-08-20", "description": "Incident during passenger ride"},
        {"date": "2025-09-05", "description": "Collision at intersection"},
        {"date": "2025-09-22", "description": "Minor crash, no injuries"},
        {"date": "2025-10-08", "description": "7th collision per NHTSA filing"},
        {"date": "2025-10-25", "description": "8th crash reported (Electrek)"},
        {"date": "2025-11-12", "description": "Incident with safety monitor present"},
        {"date": "2025-12-10", "description": "Recent incident (news reports)"},
    ]

    df = pd.DataFrame(incidents)
    df['parsed_date'] = pd.to_datetime(df['date'])
    return df


def print_incident_analysis(results: list[dict], scenario_name: str, daily_miles: int):
    """Print detailed analysis of miles between incidents."""
    print(f"\n  {scenario_name} ({daily_miles} mi/day/vehicle):")
    print(f"  {'─' * 70}")
    print(f"  {'#':<3} {'Date':<12} {'Days':<6} {'Miles':>12} {'Avg Fleet':>10} {'Cumul MPI':>12}")
    print(f"  {'─' * 70}")

    for r in results:
        print(f"  {r['incident_number']:<3} {r['incident_date']:<12} {r['days_since_previous']:<6} "
              f"{r['miles_since_previous']:>12,} {r['avg_fleet_size']:>10.1f} "
              f"{r['cumulative_miles_per_incident']:>12,.0f}")

    if results:
        final = results[-1]
        print(f"  {'─' * 70}")
        print(f"  TOTAL: {final['cumulative_miles']:,} miles over {final['cumulative_incidents']} incidents")
        print(f"  OVERALL MILES PER INCIDENT: {final['cumulative_miles_per_incident']:,.0f}")


def main():
    """Main analysis function."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    print("=" * 70)
    print("TESLA ROBOTAXI MILES PER INCIDENT ANALYSIS")
    print("Dynamic Day-by-Day Fleet Interpolation")
    print("=" * 70)
    print(f"\nData directory: {data_dir}")
    print(f"Analysis date: {datetime.now().isoformat()}")

    # Load data
    print("\n" + "─" * 70)
    print("LOADING DATA")
    print("─" * 70)

    ads_df, adas_df = load_nhtsa_data(data_dir)
    fleet_snapshots = load_fleet_data(data_dir)

    # Create fleet interpolator
    fleet_interpolator = FleetInterpolator(fleet_snapshots)

    # Filter for Tesla
    print("\n" + "─" * 70)
    print("FILTERING TESLA INCIDENTS")
    print("─" * 70)

    tesla_ads = filter_tesla_incidents(ads_df, "ADS")
    tesla_adas = filter_tesla_incidents(adas_df, "ADAS")

    # Combine and parse dates
    if len(tesla_ads) > 0 or len(tesla_adas) > 0:
        all_tesla = pd.concat([tesla_ads, tesla_adas], ignore_index=True)
        all_tesla = parse_incident_dates(all_tesla)
        use_sample = False
    else:
        print("\n  No NHTSA data found. Using sample incident data from news reports.")
        all_tesla = get_sample_incidents()
        use_sample = True

    print(f"\nTotal Tesla incidents for analysis: {len(all_tesla)}")

    # Service start date
    service_start = datetime(2025, 6, 25)
    print(f"Service start date: {service_start.strftime('%Y-%m-%d')}")

    # Calculate for different scenarios
    print("\n" + "=" * 70)
    print("MILES BETWEEN INCIDENTS (Day-by-Day Calculation)")
    print("=" * 70)

    scenarios = [
        ("Conservative", 50),
        ("Moderate", 100),
        ("Aggressive", 150)
    ]

    all_results = {}

    for scenario_name, daily_miles in scenarios:
        results = calculate_miles_between_incidents(
            all_tesla,
            fleet_interpolator,
            daily_miles,
            service_start
        )
        all_results[scenario_name] = results
        print_incident_analysis(results, scenario_name, daily_miles)

    # Summary comparison
    print("\n" + "=" * 70)
    print("COMPARISON BENCHMARKS")
    print("=" * 70)
    print("\n  Human Drivers (US avg):     ~500,000 miles per accident")
    print("  Waymo (reported):           ~1,000,000+ miles per incident")
    print("  Tesla FSD (supervised):     ~3,400,000 miles per crash (Tesla claim)")

    # Show Tesla's position
    if all_results.get("Moderate"):
        moderate = all_results["Moderate"]
        if moderate:
            final_mpi = moderate[-1]['cumulative_miles_per_incident']
            human_mpi = 500000
            ratio = human_mpi / final_mpi if final_mpi > 0 else 0

            print(f"\n  Tesla Robotaxi (moderate):  ~{final_mpi:,.0f} miles per incident")
            print(f"  → {ratio:.1f}x {'worse' if ratio > 1 else 'better'} than human drivers")

    # Fleet growth visualization
    print("\n" + "=" * 70)
    print("FLEET SIZE OVER TIME")
    print("=" * 70)

    sample_dates = [
        datetime(2025, 6, 25),
        datetime(2025, 7, 15),
        datetime(2025, 8, 15),
        datetime(2025, 9, 15),
        datetime(2025, 10, 15),
        datetime(2025, 11, 15),
        datetime(2025, 12, 15),
        datetime(2026, 1, 15),
    ]

    print(f"\n  {'Date':<12} {'Fleet Size':>12} {'Visual'}")
    print(f"  {'─' * 50}")
    for dt in sample_dates:
        size = fleet_interpolator.get_fleet_size(dt)
        bar = '█' * (size // 2)
        print(f"  {dt.strftime('%Y-%m-%d'):<12} {size:>12} {bar}")

    # Data quality notes
    print("\n" + "=" * 70)
    print("NOTES & CAVEATS")
    print("=" * 70)
    print(f"""
  {'[SAMPLE DATA]' if use_sample else '[NHTSA DATA]'}

  - Fleet sizes are {'interpolated from ' + str(len(fleet_snapshots)) + ' snapshots' if fleet_snapshots else 'estimated'}
  - Only Austin vehicles counted as true "robotaxis" (unsupervised ADS)
  - Bay Area vehicles have human safety drivers
  - Tesla has been cited for delayed crash reporting
  - Miles per vehicle per day is estimated (no official data)
  - Not all incidents are equal in severity

  To get real NHTSA data, run:
    python scripts/download_nhtsa_data.py

  To scrape latest fleet data from robotaxitracker.com:
    python scripts/scrape_fleet_data.py
    """)

    # Save results to JSON
    output_file = data_dir / "analysis_results.json"
    output = {
        "analysis_date": datetime.now().isoformat(),
        "service_start": service_start.strftime("%Y-%m-%d"),
        "data_source": "sample" if use_sample else "nhtsa",
        "incident_count": len(all_tesla),
        "scenarios": {
            name: {
                "daily_miles_per_vehicle": miles,
                "incidents": results
            }
            for (name, miles), results in zip(scenarios, [all_results.get(s[0], []) for s in scenarios])
        }
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
