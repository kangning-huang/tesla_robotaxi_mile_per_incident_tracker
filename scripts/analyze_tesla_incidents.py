#!/usr/bin/env python3
"""
Analyze Tesla Robotaxi incidents from NHTSA data and calculate miles-per-incident.

This script:
1. Loads NHTSA ADS/ADAS CSV data
2. Filters for Tesla incidents
3. Combines with fleet size data (day-by-day interpolation)
4. Calculates miles between EACH consecutive incident
5. Runs nonlinear trend analysis to detect safety improvements
6. Visualizes the MPI trend over time
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

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy import optimize
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class FleetInterpolator:
    """Interpolate fleet size for any given date based on snapshots."""

    def __init__(self, snapshots: list[dict]):
        """Initialize with fleet snapshots."""
        self.snapshots = []
        for s in snapshots:
            dt = datetime.strptime(s["date"], "%Y-%m-%d")
            count = s.get("total_robotaxi", s.get("austin_vehicles", 0))
            self.snapshots.append((dt, count))
        self.snapshots.sort(key=lambda x: x[0])

    def get_fleet_size(self, target_date: datetime) -> int:
        """Get interpolated fleet size for a specific date."""
        if not self.snapshots:
            return 25

        before = None
        after = None

        for dt, count in self.snapshots:
            if dt <= target_date:
                before = (dt, count)
            if dt >= target_date and after is None:
                after = (dt, count)

        if before is None:
            return self.snapshots[0][1]
        if after is None:
            return before[1]
        if before[0] == after[0]:
            return before[1]

        total_days = (after[0] - before[0]).days
        elapsed_days = (target_date - before[0]).days
        ratio = elapsed_days / total_days if total_days > 0 else 0

        return int(before[1] + (after[1] - before[1]) * ratio)

    def calculate_miles_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        daily_miles_per_vehicle: int,
        excluded_dates: set[str] | None = None
    ) -> tuple[int, list[dict]]:
        """Calculate total miles driven in a period with day-by-day fleet tracking.

        Args:
            excluded_dates: Set of date strings (YYYY-MM-DD) to skip (e.g. service stoppages).
        """
        total_miles = 0
        daily_breakdown = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            fleet_size = self.get_fleet_size(current_date)

            if excluded_dates and date_str in excluded_dates:
                day_miles = 0
            else:
                day_miles = fleet_size * daily_miles_per_vehicle

            total_miles += day_miles

            daily_breakdown.append({
                "date": date_str,
                "fleet_size": fleet_size,
                "daily_miles": day_miles,
                "excluded": date_str in excluded_dates if excluded_dates else False
            })

            current_date += timedelta(days=1)

        return total_miles, daily_breakdown


class MPITrendAnalyzer:
    """Analyze MPI trends using nonlinear regression."""

    def __init__(self, incident_data: list[dict]):
        """Initialize with incident MPI data."""
        self.data = incident_data
        self.days_since_start = []
        self.mpi_values = []
        self.dates = []

        if incident_data:
            start_date = datetime.strptime(incident_data[0]['incident_date'], '%Y-%m-%d')
            for d in incident_data:
                incident_date = datetime.strptime(d['incident_date'], '%Y-%m-%d')
                days = (incident_date - start_date).days
                self.days_since_start.append(days)
                self.mpi_values.append(d['mpi_since_previous'])
                self.dates.append(incident_date)

    def linear_trend(self) -> dict:
        """Fit linear trend: MPI = a + b*t"""
        if not HAS_NUMPY or len(self.mpi_values) < 2:
            return {"error": "Insufficient data or numpy not available"}

        x = np.array(self.days_since_start)
        y = np.array(self.mpi_values)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y) if HAS_SCIPY else (0, 0, 0, 1, 0)

        if not HAS_SCIPY:
            # Fallback to numpy polyfit
            coeffs = np.polyfit(x, y, 1)
            slope, intercept = coeffs[0], coeffs[1]
            r_value = np.corrcoef(x, y)[0, 1]
            p_value = None

        return {
            "type": "linear",
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "interpretation": "improving" if slope > 0 else "worsening",
            "daily_change": slope,
            "monthly_change": slope * 30
        }

    def exponential_trend(self) -> dict:
        """Fit exponential trend: MPI = a * exp(b*t)"""
        if not HAS_NUMPY or not HAS_SCIPY or len(self.mpi_values) < 3:
            return {"error": "Insufficient data or scipy not available"}

        x = np.array(self.days_since_start)
        y = np.array(self.mpi_values)

        # Exponential function
        def exp_func(t, a, b):
            return a * np.exp(b * t)

        try:
            # Initial guess
            popt, pcov = optimize.curve_fit(
                exp_func, x, y,
                p0=[y[0], 0.01],
                maxfev=5000,
                bounds=([0, -0.1], [np.inf, 0.1])
            )

            # Calculate R-squared
            y_pred = exp_func(x, *popt)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            # Doubling/halving time
            if popt[1] != 0:
                doubling_time = np.log(2) / abs(popt[1])
            else:
                doubling_time = float('inf')

            return {
                "type": "exponential",
                "a": popt[0],
                "b": popt[1],
                "r_squared": r_squared,
                "interpretation": "improving" if popt[1] > 0 else "worsening",
                "growth_rate_per_day": popt[1],
                "doubling_time_days": doubling_time if popt[1] > 0 else None,
                "halving_time_days": doubling_time if popt[1] < 0 else None
            }
        except Exception as e:
            return {"error": f"Exponential fit failed: {e}"}

    def get_best_fit(self) -> dict:
        """Determine which model fits best based on R-squared."""
        models = {}

        linear = self.linear_trend()
        if "r_squared" in linear:
            models["linear"] = linear

        exp = self.exponential_trend()
        if "r_squared" in exp:
            models["exponential"] = exp

        if not models:
            return {"error": "No models could be fitted"}

        best = max(models.items(), key=lambda x: x[1].get("r_squared", 0))
        return {
            "best_model": best[0],
            "best_fit": best[1],
            "all_models": models
        }

    def forecast(self, days_ahead: int = 30) -> dict:
        """Forecast future MPI based on best fit model."""
        best = self.get_best_fit()
        if "error" in best:
            return best

        if not HAS_NUMPY:
            return {"error": "numpy required for forecasting"}

        x_future = np.array(self.days_since_start[-1]) + np.arange(1, days_ahead + 1)

        model = best["best_fit"]
        if model["type"] == "linear":
            y_future = model["intercept"] + model["slope"] * x_future
        elif model["type"] == "exponential":
            y_future = model["a"] * np.exp(model["b"] * x_future)
        else:
            return {"error": "Unknown model type"}

        return {
            "forecast_days": days_ahead,
            "model_used": model["type"],
            "predicted_mpi_30_days": float(y_future[-1]) if len(y_future) > 0 else None,
            "trend": "improving" if y_future[-1] > self.mpi_values[-1] else "worsening"
        }


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

    make_columns = ['Make', 'MAKE', 'Manufacturer', 'MANUFACTURER', 'Vehicle Make']
    make_col = None
    for col in make_columns:
        if col in df.columns:
            make_col = col
            break

    if make_col is None:
        print(f"  Warning: Could not find make column in {system_type} data")
        return pd.DataFrame()

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


def load_service_stoppages(data_dir: Path) -> tuple[set[str], list[dict]]:
    """Load service stoppage dates from JSON.

    Returns:
        A tuple of (set of excluded date strings, list of stoppage records).
    """
    stoppages_file = data_dir / "service_stoppages.json"

    if not stoppages_file.exists():
        print(f"  No service stoppages file found: {stoppages_file}")
        return set(), []

    with open(stoppages_file) as f:
        data = json.load(f)

    stoppages = data.get("stoppages", [])
    excluded_dates = set()
    for stoppage in stoppages:
        for date_str in stoppage.get("dates", []):
            excluded_dates.add(date_str)

    print(f"  Loaded {len(stoppages)} service stoppage event(s) covering {len(excluded_dates)} day(s)")
    for stoppage in stoppages:
        dates = stoppage.get("dates", [])
        reason = stoppage.get("reason", "Unknown")
        print(f"    - {reason}: {', '.join(dates)}")

    return excluded_dates, stoppages


def calculate_mpi_between_incidents(
    incidents_df: pd.DataFrame,
    fleet_interpolator: FleetInterpolator,
    daily_miles: int,
    service_start: datetime,
    excluded_dates: set[str] | None = None
) -> list[dict]:
    """
    Calculate miles driven between EACH consecutive pair of incidents.

    Returns a list with MPI for each interval, not cumulative.
    Days in excluded_dates are skipped (0 miles accumulated).
    """
    results = []

    if incidents_df is None or len(incidents_df) == 0 or 'parsed_date' not in incidents_df.columns:
        return results

    sorted_incidents = incidents_df.dropna(subset=['parsed_date']).sort_values('parsed_date')

    if len(sorted_incidents) == 0:
        return results

    prev_date = service_start
    incident_num = 0
    cumulative_miles = 0
    cumulative_incidents = 0

    for idx, row in sorted_incidents.iterrows():
        incident_num += 1
        incident_date = row['parsed_date'].to_pydatetime()

        if incident_date < service_start:
            continue

        # Calculate miles between previous incident and this one
        miles, daily_breakdown = fleet_interpolator.calculate_miles_in_period(
            prev_date, incident_date, daily_miles, excluded_dates
        )

        days_between = (incident_date - prev_date).days
        excluded_days_in_period = sum(1 for d in daily_breakdown if d.get('excluded', False))
        active_days = days_between - excluded_days_in_period
        avg_fleet = sum(d['fleet_size'] for d in daily_breakdown) / len(daily_breakdown) if daily_breakdown else 0

        cumulative_miles += miles
        cumulative_incidents += 1

        result = {
            "incident_number": incident_num,
            "incident_date": incident_date.strftime("%Y-%m-%d"),
            "days_since_previous": days_between,
            "miles_since_previous": miles,
            "mpi_since_previous": miles,  # MPI for THIS interval only
            "avg_fleet_size": avg_fleet,
            "cumulative_miles": cumulative_miles,
            "cumulative_incidents": cumulative_incidents,
            "cumulative_mpi": cumulative_miles / cumulative_incidents
        }

        if excluded_days_in_period > 0:
            result["excluded_days"] = excluded_days_in_period
            result["active_days"] = active_days

        results.append(result)

        prev_date = incident_date

    return results


def get_sample_incidents() -> pd.DataFrame:
    """Return sample incident data based on known Tesla Robotaxi crashes."""
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


def print_mpi_analysis(results: list[dict], scenario_name: str, daily_miles: int):
    """Print detailed MPI between each consecutive incident."""
    print(f"\n  {scenario_name} ({daily_miles} mi/day/vehicle):")
    print(f"  {'─' * 75}")
    print(f"  {'#':<3} {'Date':<12} {'Days':<6} {'Fleet':>6} {'Miles Between':>14} {'MPI Interval':>12}")
    print(f"  {'─' * 75}")

    for r in results:
        print(f"  {r['incident_number']:<3} {r['incident_date']:<12} {r['days_since_previous']:<6} "
              f"{r['avg_fleet_size']:>6.0f} {r['miles_since_previous']:>14,} {r['mpi_since_previous']:>12,}")

    if results:
        final = results[-1]
        avg_mpi = sum(r['mpi_since_previous'] for r in results) / len(results)
        print(f"  {'─' * 75}")
        print(f"  AVERAGE MPI (per interval): {avg_mpi:,.0f}")
        print(f"  CUMULATIVE MPI: {final['cumulative_mpi']:,.0f}")


def print_trend_analysis(analyzer: MPITrendAnalyzer):
    """Print trend analysis results."""
    print("\n" + "=" * 75)
    print("MPI TREND ANALYSIS (Is Tesla Improving?)")
    print("=" * 75)

    if len(analyzer.mpi_values) < 3:
        print("\n  Insufficient data points for trend analysis (need at least 3)")
        return

    # Linear trend
    linear = analyzer.linear_trend()
    if "error" not in linear:
        print(f"\n  LINEAR TREND:")
        print(f"    MPI = {linear['intercept']:,.0f} + {linear['slope']:,.1f} × days")
        print(f"    R² = {linear['r_squared']:.3f}")
        print(f"    Monthly change: {linear['monthly_change']:+,.0f} miles/incident")
        print(f"    Interpretation: MPI is {linear['interpretation'].upper()}")

    # Exponential trend
    exp = analyzer.exponential_trend()
    if "error" not in exp:
        print(f"\n  EXPONENTIAL TREND:")
        print(f"    MPI = {exp['a']:,.0f} × e^({exp['b']:.6f} × days)")
        print(f"    R² = {exp['r_squared']:.3f}")
        print(f"    Daily growth rate: {exp['growth_rate_per_day']*100:+.3f}%")
        if exp.get('doubling_time_days'):
            print(f"    Doubling time: {exp['doubling_time_days']:.0f} days")
        if exp.get('halving_time_days'):
            print(f"    Halving time: {exp['halving_time_days']:.0f} days")
        print(f"    Interpretation: MPI is {exp['interpretation'].upper()}")

    # Best fit
    best = analyzer.get_best_fit()
    if "error" not in best:
        print(f"\n  BEST FIT MODEL: {best['best_model'].upper()}")
        print(f"    R² = {best['best_fit']['r_squared']:.3f}")

    # Forecast
    forecast = analyzer.forecast(days_ahead=30)
    if "error" not in forecast:
        print(f"\n  30-DAY FORECAST:")
        print(f"    Model: {forecast['model_used']}")
        print(f"    Predicted MPI: {forecast['predicted_mpi_30_days']:,.0f}")
        print(f"    Trend: {forecast['trend'].upper()}")


def plot_mpi_trend(results: list[dict], analyzer: MPITrendAnalyzer, output_path: Path):
    """Generate MPI trend visualization."""
    if not HAS_MATPLOTLIB or not HAS_NUMPY:
        print("\n  [Matplotlib/NumPy not available - skipping chart generation]")
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    dates = [datetime.strptime(r['incident_date'], '%Y-%m-%d') for r in results]
    mpi_values = [r['mpi_since_previous'] for r in results]
    cumulative_mpi = [r['cumulative_mpi'] for r in results]

    # Top chart: MPI per interval with trend line
    ax1 = axes[0]
    ax1.scatter(dates, mpi_values, s=100, c='red', alpha=0.7, label='MPI per Interval', zorder=5)
    ax1.plot(dates, mpi_values, 'r--', alpha=0.3, linewidth=1)

    # Add trend line
    if len(dates) >= 3:
        best = analyzer.get_best_fit()
        if "error" not in best:
            x_days = np.array(analyzer.days_since_start)
            x_smooth = np.linspace(x_days[0], x_days[-1], 100)

            model = best['best_fit']
            if model['type'] == 'linear':
                y_smooth = model['intercept'] + model['slope'] * x_smooth
            elif model['type'] == 'exponential':
                y_smooth = model['a'] * np.exp(model['b'] * x_smooth)
            else:
                y_smooth = None

            if y_smooth is not None:
                start_date = dates[0]
                trend_dates = [start_date + timedelta(days=int(d)) for d in x_smooth]
                ax1.plot(trend_dates, y_smooth, 'b-', linewidth=2,
                        label=f'{best["best_model"].title()} Trend (R²={model["r_squared"]:.2f})')

    ax1.axhline(y=500000, color='green', linestyle=':', linewidth=2, label='Human Driver Avg (500K)')
    ax1.set_ylabel('Miles Per Incident (MPI)', fontsize=12)
    ax1.set_title('Tesla Robotaxi: Miles Between Each Consecutive Incident', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # Bottom chart: Cumulative MPI
    ax2 = axes[1]
    ax2.fill_between(dates, cumulative_mpi, alpha=0.3, color='blue')
    ax2.plot(dates, cumulative_mpi, 'b-', linewidth=2, marker='o', label='Cumulative MPI')
    ax2.axhline(y=500000, color='green', linestyle=':', linewidth=2, label='Human Driver Avg')
    ax2.set_xlabel('Incident Date', fontsize=12)
    ax2.set_ylabel('Cumulative MPI', fontsize=12)
    ax2.set_title('Cumulative Miles Per Incident Over Time', fontsize=14)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n  Chart saved to: {output_path}")


def main():
    """Main analysis function."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    print("=" * 75)
    print("TESLA ROBOTAXI MILES PER INCIDENT ANALYSIS")
    print("With Nonlinear Trend Analysis")
    print("=" * 75)
    print(f"\nData directory: {data_dir}")
    print(f"Analysis date: {datetime.now().isoformat()}")

    # Check for optional dependencies
    print(f"\nOptional dependencies:")
    print(f"  NumPy: {'Available' if HAS_NUMPY else 'Not installed (pip install numpy)'}")
    print(f"  SciPy: {'Available' if HAS_SCIPY else 'Not installed (pip install scipy)'}")
    print(f"  Matplotlib: {'Available' if HAS_MATPLOTLIB else 'Not installed (pip install matplotlib)'}")

    # Load data
    print("\n" + "─" * 75)
    print("LOADING DATA")
    print("─" * 75)

    ads_df, adas_df = load_nhtsa_data(data_dir)
    fleet_snapshots = load_fleet_data(data_dir)
    fleet_interpolator = FleetInterpolator(fleet_snapshots)
    excluded_dates, stoppages_list = load_service_stoppages(data_dir)

    # Filter for Tesla
    print("\n" + "─" * 75)
    print("FILTERING TESLA INCIDENTS")
    print("─" * 75)

    tesla_ads = filter_tesla_incidents(ads_df, "ADS")
    tesla_adas = filter_tesla_incidents(adas_df, "ADAS")

    if len(tesla_ads) > 0 or len(tesla_adas) > 0:
        all_tesla = pd.concat([tesla_ads, tesla_adas], ignore_index=True)
        all_tesla = parse_incident_dates(all_tesla)
        use_sample = False
    else:
        print("\n  No NHTSA data found. Using sample incident data from news reports.")
        all_tesla = get_sample_incidents()
        use_sample = True

    print(f"\nTotal Tesla incidents for analysis: {len(all_tesla)}")

    service_start = datetime(2025, 6, 25)
    print(f"Service start date: {service_start.strftime('%Y-%m-%d')}")

    # Calculate MPI for moderate scenario (primary)
    print("\n" + "=" * 75)
    print("MPI BETWEEN CONSECUTIVE INCIDENTS")
    print("=" * 75)

    daily_miles = 115  # Moderate scenario (based on Tesla's 250K miles / 97 days / ~20 vehicles)
    results = calculate_mpi_between_incidents(all_tesla, fleet_interpolator, daily_miles, service_start, excluded_dates)

    print_mpi_analysis(results, "Moderate", daily_miles)

    # Trend analysis
    if results:
        analyzer = MPITrendAnalyzer(results)
        print_trend_analysis(analyzer)

        # Generate chart
        chart_path = data_dir / "mpi_trend_chart.png"
        plot_mpi_trend(results, analyzer, chart_path)

    # Comparison
    print("\n" + "=" * 75)
    print("COMPARISON BENCHMARKS")
    print("=" * 75)
    print("\n  Human Drivers (US avg):     ~500,000 miles per accident")
    print("  Waymo (reported):           ~1,000,000+ miles per incident")
    print("  Tesla FSD (supervised):     ~3,400,000 miles per crash (Tesla claim)")

    if results:
        avg_mpi = sum(r['mpi_since_previous'] for r in results) / len(results)
        latest_mpi = results[-1]['mpi_since_previous']
        human_mpi = 500000

        print(f"\n  Tesla Robotaxi (average):   ~{avg_mpi:,.0f} miles per incident")
        print(f"  Tesla Robotaxi (latest):    ~{latest_mpi:,.0f} miles per incident")
        print(f"  → {human_mpi / avg_mpi:.1f}x worse than human drivers (average)")
        print(f"  → {human_mpi / latest_mpi:.1f}x worse than human drivers (latest)")

    # Fleet visualization
    print("\n" + "=" * 75)
    print("FLEET SIZE OVER TIME")
    print("=" * 75)

    sample_dates = [
        datetime(2025, 6, 25), datetime(2025, 7, 15), datetime(2025, 8, 15),
        datetime(2025, 9, 15), datetime(2025, 10, 15), datetime(2025, 11, 15),
        datetime(2025, 12, 15), datetime(2026, 1, 15),
    ]

    print(f"\n  {'Date':<12} {'Fleet Size':>12} {'Visual'}")
    print(f"  {'─' * 50}")
    for dt in sample_dates:
        size = fleet_interpolator.get_fleet_size(dt)
        bar = '█' * (size // 2)
        print(f"  {dt.strftime('%Y-%m-%d'):<12} {size:>12} {bar}")

    # Notes
    print("\n" + "=" * 75)
    print("NOTES & METHODOLOGY")
    print("=" * 75)
    print(f"""
  {'[SAMPLE DATA]' if use_sample else '[NHTSA DATA]'}

  MPI Calculation:
  - Miles between incident N and N+1 = Σ(daily_fleet_size × miles_per_day)
  - Fleet size interpolated daily from {len(fleet_snapshots)} snapshots
  - Assumes {daily_miles} miles/vehicle/day (moderate estimate)
  - Service stoppage days excluded: {len(excluded_dates)} day(s) with 0 miles

  Trend Analysis:
  - Linear: MPI = a + b×t (constant rate of change)
  - Exponential: MPI = a×e^(bt) (percentage growth/decay)
  - Best model selected by highest R² value

  Caveats:
  - Tesla cited for delayed crash reporting to NHTSA
  - Fleet size estimates may differ from actual active vehicles
  - Not all incidents are equal in severity
  - Small sample size limits trend reliability
    """)

    # Save results
    output_file = data_dir / "analysis_results.json"
    trend_data = {}
    if results:
        analyzer = MPITrendAnalyzer(results)
        trend_data = analyzer.get_best_fit()

    # Build stoppage summary for output
    stoppage_summary = []
    for stoppage in stoppages_list:
        stoppage_summary.append({
            "dates": stoppage.get("dates", []),
            "reason": stoppage.get("reason", "Unknown")
        })

    output = {
        "analysis_date": datetime.now().isoformat(),
        "service_start": service_start.strftime("%Y-%m-%d"),
        "data_source": "sample" if use_sample else "nhtsa",
        "incident_count": len(all_tesla),
        "daily_miles_assumption": daily_miles,
        "excluded_dates": sorted(excluded_dates),
        "service_stoppages": stoppage_summary,
        "incidents": results,
        "trend_analysis": trend_data,
        "summary": {
            "average_mpi": sum(r['mpi_since_previous'] for r in results) / len(results) if results else 0,
            "latest_mpi": results[-1]['mpi_since_previous'] if results else 0,
            "cumulative_mpi": results[-1]['cumulative_mpi'] if results else 0,
            "total_miles": results[-1]['cumulative_miles'] if results else 0,
            "total_excluded_days": len(excluded_dates)
        }
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
