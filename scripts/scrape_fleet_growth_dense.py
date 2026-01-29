#!/usr/bin/env python3
"""
Dense hover scraper variant for fleet growth data from robotaxitracker.com.

This variant addresses the problem that the standard scraper
(scrape_fleet_growth.py) misses early data points (June-July 2025).

Root cause analysis:
    The original hover strategy uses 100 sample positions across the full chart
    width with a 60px left margin. Over ~7 months of data, each step covers
    ~2 days. Early bars (June-July 2025) are thin and sparse in the bar chart,
    so many fall between hover positions. Additionally:
      - The 60px left margin can skip the very first bars
      - A single hover Y position at 40% height may miss short bars
        (early fleet was ~10 vehicles, so bars are very short)

Improvements in this variant:
    1. Reduced left margin (30px instead of 60px) to reach earliest bars
    2. Multi-pass hovering:
       - Pass 1: Dense sweep of early region (first 30% of chart) with
         pixel-by-pixel steps to catch every bar
       - Pass 2: Full chart sweep with 300 samples (3x original density)
    3. Multiple Y heights per position to catch short bars
    4. Merges results from all passes via deduplication

Usage:
    python scripts/scrape_fleet_growth_dense.py

This script does NOT overwrite the existing fleet_growth_active.json.
It writes to fleet_growth_active_dense.json for comparison/testing.
"""

import asyncio
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright is required. Install with:")
    print("  pip install playwright && playwright install chromium")
    sys.exit(1)

# Re-use helpers from the existing scraper
from scrape_fleet_growth import (
    click_fleet_tab,
    deduplicate_by_date,
    extract_chart_data_from_react,
    extract_fleet_data_from_api_responses,
    parse_tooltip_text as _parse_tooltip_text_base,
    scroll_and_wait_for_charts,
    validate_data,
)


def parse_tooltip_text(text: str) -> dict | None:
    """Enhanced tooltip parser that also handles Chinese date format (YYYY年M月D日).

    Wraps the original parse_tooltip_text and adds support for CJK date formats
    that may appear when the site is viewed in Chinese locale.
    """
    if not text:
        return None

    # Try the original parser first
    result = _parse_tooltip_text_base(text)
    if result:
        return result

    # Try Chinese date format: 2025年6月22日
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if m:
        date_str = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        result = {"date": date_str}

        # Extract counts (same logic as original)
        austin_m = re.search(r"Austin\s*(\d+)", text, re.IGNORECASE)
        bay_m = re.search(r"Bay\s*Area\s*(\d+)", text, re.IGNORECASE)

        if austin_m:
            result["austin"] = int(austin_m.group(1))
        if bay_m:
            result["bayarea"] = int(bay_m.group(1))

        if "austin" in result or "bayarea" in result:
            return result

    return None

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_JSON = DATA_DIR / "fleet_growth_active_dense.json"
OUTPUT_CSV = DATA_DIR / "fleet_growth_active_dense.csv"
URL = "https://robotaxitracker.com"


async def _read_tooltip(page) -> str | None:
    """Read the current tooltip text, returning None if hidden/empty."""
    return await page.evaluate("""
        () => {
            const el = document.querySelector('.recharts-tooltip-wrapper');
            if (!el) return null;
            const style = window.getComputedStyle(el);
            if (style.visibility === 'hidden' || style.opacity === '0') return null;
            const text = el.textContent || '';
            return text.trim().length > 0 ? text.trim() : null;
        }
    """)


async def _get_chart_bbox(page) -> dict | None:
    """Find the Fleet Growth chart and return its bounding box."""
    # First scroll it into view
    scrolled = await page.evaluate("""
        () => {
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, span, p');
            let headingEl = null;
            for (const el of headings) {
                const text = (el.textContent || '').trim();
                if (text === 'Fleet Growth' && el.children.length < 5) {
                    headingEl = el;
                    break;
                }
            }

            const allCharts = document.querySelectorAll('.recharts-wrapper');
            if (allCharts.length === 0) return null;

            const charts = [];
            for (const chart of allCharts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) charts.push(chart);
            }
            if (charts.length === 0) return null;

            let target = null;
            if (headingEl) {
                const headingRect = headingEl.getBoundingClientRect();
                let bestDist = Infinity;
                for (const chart of charts) {
                    const rect = chart.getBoundingClientRect();
                    const dist = Math.abs(rect.top - headingRect.bottom);
                    if (dist < bestDist && rect.top >= headingRect.top - 50) {
                        bestDist = dist;
                        target = chart;
                    }
                }
            }
            if (!target) target = charts[0];

            target.scrollIntoView({block: 'center', behavior: 'instant'});
            return true;
        }
    """)

    if not scrolled:
        return None

    await asyncio.sleep(1)

    # Re-read bbox after scroll
    return await page.evaluate("""
        () => {
            const allCharts = document.querySelectorAll('.recharts-wrapper');
            for (const chart of allCharts) {
                const rect = chart.getBoundingClientRect();
                if (rect.height >= 100 && rect.width >= 200) {
                    const svg = chart.querySelector('svg.recharts-surface');
                    const el = svg || chart;
                    const r = el.getBoundingClientRect();
                    return {x: r.x, y: r.y, width: r.width, height: r.height};
                }
            }
            return null;
        }
    """)


async def _hover_pass(page, bbox, x_start, x_end, num_positions, y_fractions,
                       seen_dates, label="") -> list:
    """Perform a single hover pass across a region of the chart.

    Args:
        page: Playwright page.
        bbox: Chart bounding box dict with x, y, width, height.
        x_start: Left x-coordinate to start hovering.
        x_end: Right x-coordinate to stop hovering.
        num_positions: Number of evenly-spaced x positions to hover.
        y_fractions: List of Y positions as fractions of chart height to try.
        seen_dates: Set of already-captured date strings (mutated in-place).
        label: Label for logging.

    Returns:
        List of newly captured data points.
    """
    results = []
    step = (x_end - x_start) / max(num_positions - 1, 1)
    prefix = f"[{label}] " if label else ""

    print(f"  {prefix}Hovering {num_positions} positions from x={x_start:.0f} to x={x_end:.0f}, "
          f"{len(y_fractions)} Y heights")

    # Activate chart
    first_y = bbox["y"] + bbox["height"] * y_fractions[0]
    await page.mouse.move(x_start, first_y)
    await asyncio.sleep(0.5)

    for i in range(num_positions):
        x = x_start + (i * step)

        for y_frac in y_fractions:
            y = bbox["y"] + bbox["height"] * y_frac
            await page.mouse.move(x, y)
            await asyncio.sleep(0.08)

            tooltip_text = await _read_tooltip(page)
            if not tooltip_text:
                continue

            dp = parse_tooltip_text(tooltip_text)
            if dp and dp.get("date") and dp["date"] not in seen_dates:
                seen_dates.add(dp["date"])
                results.append(dp)
                if len(results) <= 5 or len(results) % 10 == 0:
                    print(f"    {prefix}[{len(results)}] {dp['date']} - "
                          f"Austin: {dp.get('austin')}, Bay: {dp.get('bayarea')}")
                # Found a tooltip at this x, no need to try other Y heights
                break

    return results


async def extract_data_via_dense_hover(page) -> list:
    """Dense multi-pass hover extraction targeting full date coverage.

    Pass 1: Pixel-level sweep of the early region (first 30% of chart)
            to catch the sparse, thin bars from June-August 2025.
    Pass 2: Full chart sweep with 300 positions (3x standard density).
    Pass 3: If early dates still missing, retry early region with different
            Y heights to catch very short bars.
    """
    bbox = await _get_chart_bbox(page)
    if not bbox:
        print("  Could not find chart element for hover")
        return []

    print(f"  Chart bbox: x={bbox['x']:.0f}, y={bbox['y']:.0f}, "
          f"w={bbox['width']:.0f}, h={bbox['height']:.0f}")

    # Reduced left margin to reach earliest bars (30px instead of 60px)
    chart_left = bbox["x"] + 30
    chart_right = bbox["x"] + bbox["width"] - 10

    # The early region boundary (~30% of chart width covers June-Sept 2025)
    early_boundary = chart_left + (chart_right - chart_left) * 0.30
    chart_width_px = chart_right - chart_left
    early_width_px = early_boundary - chart_left

    seen_dates = set()
    all_results = []

    # --- Pass 1: Dense sweep of early region ---
    # Pixel-by-pixel (every 2 pixels) to catch every thin bar
    early_positions = max(int(early_width_px / 2), 50)
    pass1 = await _hover_pass(
        page, bbox,
        x_start=chart_left,
        x_end=early_boundary,
        num_positions=early_positions,
        y_fractions=[0.4, 0.7, 0.2],  # mid, low, high - short bars need low Y
        seen_dates=seen_dates,
        label="Pass1-early"
    )
    all_results.extend(pass1)
    print(f"  Pass 1 (early region): {len(pass1)} new dates captured")

    # --- Pass 2: Full chart dense sweep ---
    pass2 = await _hover_pass(
        page, bbox,
        x_start=chart_left,
        x_end=chart_right,
        num_positions=300,
        y_fractions=[0.4, 0.7],
        seen_dates=seen_dates,
        label="Pass2-full"
    )
    all_results.extend(pass2)
    print(f"  Pass 2 (full chart): {len(pass2)} new dates captured")

    # --- Pass 3: If we're still missing very early dates, try extreme sweep ---
    # Check if we have any dates before 2025-08-01
    early_dates = [d for d in all_results
                   if d.get("date", "") < "2025-08-01"]
    if len(early_dates) < 3:
        print(f"  Only {len(early_dates)} dates before 2025-08-01, running extra-early sweep...")

        # Sweep just the first 15% of chart with pixel-level precision
        ultra_early_boundary = chart_left + chart_width_px * 0.15
        ultra_positions = max(int((ultra_early_boundary - chart_left) / 1.5), 40)

        pass3 = await _hover_pass(
            page, bbox,
            x_start=chart_left - 10,  # Even further left to catch edge bars
            x_end=ultra_early_boundary,
            num_positions=ultra_positions,
            y_fractions=[0.8, 0.6, 0.4, 0.2, 0.9],  # Many Y heights
            seen_dates=seen_dates,
            label="Pass3-ultra-early"
        )
        all_results.extend(pass3)
        print(f"  Pass 3 (ultra-early): {len(pass3)} new dates captured")

    await page.mouse.move(0, 0)

    total_unique = len(seen_dates)
    print(f"\n  Dense hover total: {total_unique} unique dates captured")
    return all_results


async def scrape_active_fleet_dense():
    """Scrape active fleet data with dense hover strategy."""
    captured_api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # Intercept API responses
        async def capture_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            if "json" in ct and "/api/" in url:
                try:
                    body = await response.text()
                    captured_api_responses.append({"url": url, "body": body})
                except Exception:
                    pass

        page.on("response", capture_response)

        print("Loading robotaxitracker.com...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)

        print("Waiting for charts to render...")
        await scroll_and_wait_for_charts(page)

        # Click Active tab
        print("\n" + "=" * 60)
        print("Scraping ACTIVE fleet growth (dense hover)")
        print("=" * 60)
        await click_fleet_tab(page, "Active")

        # Try Strategy 1 & 2 first (they might return full data)
        print("\n  Strategy 1: API responses")
        data = extract_fleet_data_from_api_responses(captured_api_responses)
        if data:
            data = deduplicate_by_date(data)
            if validate_data(data):
                early = [d for d in data if d.get("date", "") < "2025-08-01"]
                if len(early) >= 3:
                    print(f"  API returned {len(data)} points with {len(early)} early dates - sufficient!")
                    await browser.close()
                    return data
                print(f"  API returned {len(data)} points but only {len(early)} early dates")

        print("\n  Strategy 2: React fiber")
        react_data = await extract_chart_data_from_react(page)
        if react_data:
            react_data = deduplicate_by_date(react_data)
            if validate_data(react_data):
                early = [d for d in react_data if d.get("date", "") < "2025-08-01"]
                if len(early) >= 3:
                    print(f"  React returned {len(react_data)} points with {len(early)} early dates - sufficient!")
                    await browser.close()
                    return react_data
                print(f"  React returned {len(react_data)} points but only {len(early)} early dates")

        # Strategy 3: Dense hover (the main improvement)
        print("\n  Strategy 3: Dense multi-pass hover")
        hover_data = await extract_data_via_dense_hover(page)

        # Merge all sources
        all_data = []
        if data:
            all_data.extend(data)
        if react_data:
            all_data.extend(react_data)
        if hover_data:
            all_data.extend(hover_data)

        all_data = deduplicate_by_date(all_data)

        await browser.close()

    return all_data


def print_comparison(dense_data, existing_data):
    """Print comparison between dense scrape and existing data."""
    print("\n" + "=" * 60)
    print("COMPARISON: Dense vs Existing")
    print("=" * 60)

    existing_dates = {d["date"] for d in existing_data}
    dense_dates = {d.get("date") for d in dense_data}

    new_dates = dense_dates - existing_dates
    missing_dates = existing_dates - dense_dates

    print(f"  Existing data: {len(existing_data)} dates "
          f"({existing_data[0]['date']} to {existing_data[-1]['date']})")
    print(f"  Dense scrape:  {len(dense_data)} dates "
          f"({dense_data[0].get('date', '?')} to {dense_data[-1].get('date', '?')})")
    print(f"  New dates found: {len(new_dates)}")
    print(f"  Missing from dense: {len(missing_dates)}")

    if new_dates:
        print(f"\n  New dates (not in existing):")
        for d in sorted(new_dates):
            match = next((x for x in dense_data if x.get("date") == d), {})
            print(f"    {d}  Austin: {match.get('austin', '?')}")

    if missing_dates:
        print(f"\n  Missing (in existing but not dense):")
        for d in sorted(missing_dates):
            print(f"    {d}")

    # Show early data specifically
    early_existing = [d for d in existing_data if d["date"] < "2025-08-01"]
    early_dense = [d for d in dense_data if d.get("date", "") < "2025-08-01"]
    print(f"\n  Early dates (before Aug 2025):")
    print(f"    Existing: {len(early_existing)} - {[d['date'] for d in early_existing]}")
    print(f"    Dense:    {len(early_dense)} - {[d.get('date') for d in early_dense]}")


async def main():
    print("=" * 60)
    print("Dense Fleet Growth Scraper (targeting early dates)")
    print("=" * 60)
    print()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    dense_data = await scrape_active_fleet_dense()

    if not dense_data:
        print("\nFAILED: No data extracted")
        sys.exit(1)

    if not validate_data(dense_data):
        print(f"\nFAILED: Data validation failed ({len(dense_data)} points)")
        sys.exit(1)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"DENSE ACTIVE FLEET: {len(dense_data)} data points")
    print(f"{'=' * 60}")
    print(f"Date range: {dense_data[0].get('date')} to {dense_data[-1].get('date')}")
    print(f"\nAll entries:")
    for d in dense_data:
        print(f"  {d.get('date')}  Austin: {str(d.get('austin', '-')):>4}")

    # Compare with existing
    existing_path = DATA_DIR / "fleet_growth_active.json"
    if existing_path.exists():
        with open(existing_path) as f:
            existing = json.load(f).get("data", [])
        print_comparison(dense_data, existing)

    # Save to separate file (NOT overwriting existing)
    output = {
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
        "source": "robotaxitracker.com",
        "description": "Active fleet growth - dense hover scrape (targeting early dates)",
        "data_points": len(dense_data),
        "data": dense_data,
    }
    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  JSON saved: {OUTPUT_JSON}")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "austin", "bayarea", "total"])
        writer.writeheader()
        for row in dense_data:
            writer.writerow(row)
    print(f"  CSV saved:  {OUTPUT_CSV}")

    # Report success/failure on early dates
    early = [d for d in dense_data if d.get("date", "") < "2025-08-01"]
    if early:
        print(f"\n  SUCCESS: Captured {len(early)} early dates (before Aug 2025)")
    else:
        print(f"\n  WARNING: Still no early dates captured. The chart may need "
              f"a different interaction method (zoom, scroll, etc.)")


if __name__ == "__main__":
    asyncio.run(main())
