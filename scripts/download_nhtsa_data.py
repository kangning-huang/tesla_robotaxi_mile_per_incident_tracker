#!/usr/bin/env python3
"""
Download NHTSA Standing General Order (SGO) crash data for autonomous vehicles.

This script downloads the official CSV files from NHTSA containing:
- ADS (Automated Driving Systems) incident reports - Level 3-5 autonomy
- ADAS (Advanced Driver Assistance Systems) incident reports - Level 2 (FSD, Autopilot)

Data is updated monthly by NHTSA.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Try to use requests if available, fall back to urllib
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    USE_REQUESTS = False

# NHTSA SGO Data URLs
NHTSA_BASE_URL = "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01"

DATA_FILES = {
    "ADS": {
        "url": f"{NHTSA_BASE_URL}/SGO-2021-01_Incident_Reports_ADS.csv",
        "filename": "SGO-2021-01_Incident_Reports_ADS.csv",
        "description": "Automated Driving Systems (L3-L5) - Robotaxi incidents"
    },
    "ADAS": {
        "url": f"{NHTSA_BASE_URL}/SGO-2021-01_Incident_Reports_ADAS.csv",
        "filename": "SGO-2021-01_Incident_Reports_ADAS.csv",
        "description": "Level 2 ADAS (FSD, Autopilot) incidents"
    },
    "DATA_DICTIONARY": {
        "url": f"{NHTSA_BASE_URL}/SGO-2021-01_Data_Element_Definitions.pdf",
        "filename": "SGO-2021-01_Data_Element_Definitions.pdf",
        "description": "Data field definitions (122 columns)"
    }
}

# Archive data (pre-June 2025)
ARCHIVE_FILES = {
    "ADS_ARCHIVE": {
        "url": f"{NHTSA_BASE_URL}/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv",
        "filename": "archive/SGO-2021-01_Incident_Reports_ADS_archive.csv",
        "description": "Historical ADS data (2021 - June 2025)"
    },
    "ADAS_ARCHIVE": {
        "url": f"{NHTSA_BASE_URL}/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADAS.csv",
        "filename": "archive/SGO-2021-01_Incident_Reports_ADAS_archive.csv",
        "description": "Historical ADAS data (2021 - June 2025)"
    }
}


def download_file(url: str, filepath: Path, description: str) -> bool:
    """Download a file from URL to filepath."""
    print(f"Downloading: {description}")
    print(f"  URL: {url}")
    print(f"  To: {filepath}")

    # Create parent directories if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        if USE_REQUESTS:
            response = requests.get(url, timeout=60, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NHTSA-Data-Downloader/1.0)'
            })
            response.raise_for_status()
            filepath.write_bytes(response.content)
            size = len(response.content)
        else:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NHTSA-Data-Downloader/1.0)'
            })
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
                filepath.write_bytes(data)
                size = len(data)

        print(f"  ✓ Downloaded {size:,} bytes")
        return True

    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Download all NHTSA SGO data files."""
    # Determine data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    print("=" * 60)
    print("NHTSA Standing General Order (SGO) Data Downloader")
    print("=" * 60)
    print(f"\nData directory: {data_dir}")
    print(f"Download time: {datetime.now().isoformat()}")
    print()

    # Download current data files
    print("=" * 60)
    print("CURRENT DATA FILES")
    print("=" * 60)

    success_count = 0
    total_count = 0

    for name, info in DATA_FILES.items():
        total_count += 1
        filepath = data_dir / info["filename"]
        if download_file(info["url"], filepath, info["description"]):
            success_count += 1
        print()

    # Download archive files
    print("=" * 60)
    print("ARCHIVE DATA FILES (2021 - June 2025)")
    print("=" * 60)

    for name, info in ARCHIVE_FILES.items():
        total_count += 1
        filepath = data_dir / info["filename"]
        if download_file(info["url"], filepath, info["description"]):
            success_count += 1
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Downloaded: {success_count}/{total_count} files")

    if success_count == total_count:
        print("\n✓ All files downloaded successfully!")
        print("\nNext steps:")
        print("  1. Run: python scripts/analyze_tesla_incidents.py")
        print("  2. View the miles-per-incident metrics")
    else:
        print("\n⚠ Some downloads failed. Check your internet connection.")
        print("You can also download files manually from:")
        print(f"  {NHTSA_BASE_URL}/")

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
