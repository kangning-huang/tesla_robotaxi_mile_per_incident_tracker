#!/usr/bin/env python3
"""
Scrape Tesla Robotaxi fleet size data from robotaxitracker.com

This script uses Playwright to:
1. Navigate to robotaxitracker.com
2. Extract current fleet size data
3. Extract historical fleet growth data if available
4. Save to JSON for analysis

The site pings Tesla's API every 5 minutes and tracks:
- Number of vehicles in Austin and Bay Area
- Wait times and availability
- Historical fleet growth

Usage:
    pip install playwright
    playwright install chromium
    python scrape_fleet_data.py
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: playwright is required. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


# Output file
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "fleet_data_scraped.json"

# URLs
ROBOTAXI_TRACKER_URL = "https://robotaxitracker.com"
NHTSA_PAGE_URL = "https://robotaxitracker.com/nhtsa"


async def scroll_and_wait_for_charts(page):
    """Scroll through the page to trigger lazy-loaded charts."""
    print("  Scrolling to trigger lazy-loaded content...")

    # Get page height
    page_height = await page.evaluate("document.body.scrollHeight")
    viewport_height = 1080

    # Scroll down in steps to trigger IntersectionObserver for lazy elements
    current_position = 0
    while current_position < page_height:
        current_position += viewport_height // 2
        await page.evaluate(f"window.scrollTo(0, {current_position})")
        await asyncio.sleep(0.5)  # Wait for lazy content to load

    # Scroll back to top
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)

    # Now scroll specifically to Fleet Growth section and wait
    try:
        fleet_section = await page.query_selector("text=Fleet Growth")
        if fleet_section:
            await fleet_section.scroll_into_view_if_needed()
            print("  Found Fleet Growth section, waiting for chart...")
            await asyncio.sleep(2)  # Wait for chart animation to complete
    except Exception as e:
        print(f"  Could not scroll to Fleet Growth: {e}")

    # Wait for any canvas or SVG charts to render
    try:
        await page.wait_for_selector("canvas, svg path", timeout=5000)
        print("  Chart elements detected")
        await asyncio.sleep(1)  # Extra wait for chart data to populate
    except Exception:
        print("  No chart canvas/SVG found within timeout")


async def extract_fleet_numbers(page) -> dict:
    """Extract fleet size numbers from the page."""
    fleet_data = {
        "austin_vehicles": None,
        "bayarea_vehicles": None,
        "total_vehicles": None,
        "austin_available": None,
        "bayarea_available": None,
    }

    # Wait for page to load dynamic content
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)  # Extra wait for JS rendering

    # Scroll through page to trigger lazy-loaded charts
    await scroll_and_wait_for_charts(page)

    # Get page content
    content = await page.content()

    # Try to find fleet numbers using various patterns
    # Pattern 1: Look for specific text patterns (based on robotaxitracker.com layout)
    patterns = [
        # Fleet Growth section patterns: "TOTAL FLEET" "BAY AREA" "AUSTIN" followed by numbers
        (r"TOTAL\s*FLEET\s*(\d+)", "total_vehicles"),
        (r"BAY\s*AREA\s*(\d+)", "bayarea_vehicles"),
        (r"AUSTIN\s*(\d+)", "austin_vehicles"),
        # Alternative patterns
        (r"Austin[:\s]*(\d+)\s*(?:vehicles?|cars?)?", "austin_vehicles"),
        (r"Bay\s*Area[:\s]*(\d+)\s*(?:vehicles?|cars?)?", "bayarea_vehicles"),
        (r"Total[:\s]*(\d+)\s*(?:vehicles?|cars?|robotaxis?)?", "total_vehicles"),
        (r"(\d+)\s*(?:vehicles?|cars?)\s*(?:in\s*)?Austin", "austin_vehicles"),
        (r"(\d+)\s*(?:vehicles?|cars?)\s*(?:in\s*)?(?:Bay\s*Area|SF|San\s*Francisco)", "bayarea_vehicles"),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match and fleet_data[key] is None:
            fleet_data[key] = int(match.group(1))

    # Try to extract from specific elements using JavaScript evaluation
    # This handles dynamic React/Vue components better
    try:
        js_extraction = """
        () => {
            const result = {};
            // Look for text containing fleet numbers in the Fleet Growth section
            const allText = document.body.innerText;

            // Pattern: TOTAL FLEET followed by number on next line or nearby
            const totalMatch = allText.match(/TOTAL\\s*FLEET[\\s\\n]*(\\d+)/i);
            if (totalMatch) result.total = parseInt(totalMatch[1]);

            const bayMatch = allText.match(/BAY\\s*AREA[\\s\\n]*(\\d+)/i);
            if (bayMatch) result.bayarea = parseInt(bayMatch[1]);

            const austinMatch = allText.match(/AUSTIN[\\s\\n]*(\\d+)/i);
            if (austinMatch) result.austin = parseInt(austinMatch[1]);

            return result;
        }
        """
        js_result = await page.evaluate(js_extraction)
        if js_result:
            if js_result.get("total") and fleet_data["total_vehicles"] is None:
                fleet_data["total_vehicles"] = js_result["total"]
            if js_result.get("bayarea") and fleet_data["bayarea_vehicles"] is None:
                fleet_data["bayarea_vehicles"] = js_result["bayarea"]
            if js_result.get("austin") and fleet_data["austin_vehicles"] is None:
                fleet_data["austin_vehicles"] = js_result["austin"]
    except Exception as e:
        print(f"  JS extraction failed: {e}")

    # Try to extract from specific elements
    selectors_to_try = [
        # Common dashboard element patterns
        (".fleet-count", "total_vehicles"),
        (".austin-count", "austin_vehicles"),
        (".bayarea-count", "bayarea_vehicles"),
        ("[data-fleet-austin]", "austin_vehicles"),
        ("[data-fleet-bayarea]", "bayarea_vehicles"),
        # Stats cards
        (".stat-card:has-text('Austin') .stat-value", "austin_vehicles"),
        (".stat-card:has-text('Bay') .stat-value", "bayarea_vehicles"),
    ]

    for selector, key in selectors_to_try:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                numbers = re.findall(r'\d+', text)
                if numbers and fleet_data[key] is None:
                    fleet_data[key] = int(numbers[0])
        except Exception:
            pass

    # Calculate total if we have components
    if fleet_data["austin_vehicles"] and fleet_data["bayarea_vehicles"]:
        fleet_data["total_vehicles"] = fleet_data["austin_vehicles"] + fleet_data["bayarea_vehicles"]

    return fleet_data


async def extract_historical_data(page) -> list:
    """Try to extract historical fleet data from charts or tables."""
    historical = []

    try:
        # Look for chart data in script tags or data attributes
        scripts = await page.query_selector_all("script")
        for script in scripts:
            content = await script.text_content()
            if content and ("chartData" in content or "fleetHistory" in content or "dates" in content):
                # Try to parse JSON data from chart configs
                json_matches = re.findall(r'\{[^{}]*"dates?"[^{}]*\}', content)
                for match in json_matches:
                    try:
                        data = json.loads(match)
                        if "date" in data or "dates" in data:
                            historical.append(data)
                    except json.JSONDecodeError:
                        pass

        # Look for data tables
        tables = await page.query_selector_all("table")
        for table in tables:
            rows = await table.query_selector_all("tr")
            for row in rows:
                cells = await row.query_selector_all("td, th")
                if len(cells) >= 2:
                    cell_texts = [await c.text_content() for c in cells]
                    # Check if first cell looks like a date
                    if cell_texts[0] and re.match(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}', cell_texts[0].strip()):
                        historical.append({
                            "date": cell_texts[0].strip(),
                            "value": cell_texts[1].strip() if len(cell_texts) > 1 else None
                        })

    except Exception as e:
        print(f"Warning: Could not extract historical data: {e}")

    return historical


async def extract_nhtsa_incidents(page) -> list:
    """Extract NHTSA incident data from the /nhtsa page."""
    incidents = []

    try:
        await page.goto(NHTSA_PAGE_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Look for incident rows/cards
        incident_selectors = [
            ".incident-row",
            ".incident-card",
            "[data-incident]",
            "table tr",
            ".crash-report",
        ]

        for selector in incident_selectors:
            elements = await page.query_selector_all(selector)
            if elements and len(elements) > 1:  # More than header row
                for elem in elements[1:]:  # Skip header
                    text = await elem.text_content()
                    if text and ("Tesla" in text or "crash" in text.lower() or "incident" in text.lower()):
                        # Try to parse date
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})', text)
                        incidents.append({
                            "raw_text": text.strip()[:500],
                            "date": date_match.group(1) if date_match else None,
                            "source": "robotaxitracker.com/nhtsa"
                        })
                break

    except Exception as e:
        print(f"Warning: Could not extract NHTSA data: {e}")

    return incidents


async def take_screenshot(page, name: str):
    """Take a screenshot for debugging."""
    screenshot_path = DATA_DIR / f"screenshot_{name}.png"
    await page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"Screenshot saved: {screenshot_path}")


async def scrape_robotaxi_tracker():
    """Main scraping function."""
    print("=" * 60)
    print("ROBOTAXI TRACKER SCRAPER")
    print("=" * 60)
    print(f"\nTarget: {ROBOTAXI_TRACKER_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser
        print("\nLaunching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        try:
            # Navigate to main page
            print(f"\nNavigating to {ROBOTAXI_TRACKER_URL}...")
            await page.goto(ROBOTAXI_TRACKER_URL, wait_until="domcontentloaded", timeout=30000)

            # Wait for initial load
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            # Take initial screenshot (before scrolling)
            await take_screenshot(page, "main_page_initial")

            # Extract fleet data (this now includes scrolling to trigger lazy content)
            print("\nExtracting fleet data...")
            fleet_data = await extract_fleet_numbers(page)
            print(f"  Austin vehicles: {fleet_data['austin_vehicles']}")
            print(f"  Bay Area vehicles: {fleet_data['bayarea_vehicles']}")
            print(f"  Total vehicles: {fleet_data['total_vehicles']}")

            # Scroll to Fleet Growth section and take screenshot
            try:
                fleet_section = await page.query_selector("text=Fleet Growth")
                if fleet_section:
                    await fleet_section.scroll_into_view_if_needed()
                    await asyncio.sleep(2)  # Wait for chart to render
                    await take_screenshot(page, "fleet_growth_section")
            except Exception as e:
                print(f"  Could not screenshot Fleet Growth section: {e}")

            # Take full page screenshot after all content loaded
            await take_screenshot(page, "main_page_full")

            # Extract historical data
            print("\nExtracting historical data...")
            historical = await extract_historical_data(page)
            print(f"  Found {len(historical)} historical data points")

            # Extract NHTSA incidents
            print("\nExtracting NHTSA incidents...")
            incidents = await extract_nhtsa_incidents(page)
            print(f"  Found {len(incidents)} incidents")

            # Take screenshot of NHTSA page
            await take_screenshot(page, "nhtsa_page")

            # Compile results
            result = {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "source": ROBOTAXI_TRACKER_URL,
                    "scraper_version": "1.0.0"
                },
                "current_fleet": fleet_data,
                "historical_data": historical,
                "nhtsa_incidents": incidents
            }

            # Save to file
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nData saved to: {OUTPUT_FILE}")

            return result

        except PlaywrightTimeout as e:
            print(f"\nTimeout error: {e}")
            print("The site may be blocking automated access.")
            await take_screenshot(page, "error_timeout")
            return None

        except Exception as e:
            print(f"\nError during scraping: {e}")
            await take_screenshot(page, "error")
            raise

        finally:
            await browser.close()
            print("\nBrowser closed.")


def main():
    """Entry point."""
    result = asyncio.run(scrape_robotaxi_tracker())

    if result:
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)

        if result["current_fleet"]["total_vehicles"]:
            print(f"\nCurrent Fleet Size: {result['current_fleet']['total_vehicles']}")
        else:
            print("\nWarning: Could not extract fleet numbers.")
            print("Check screenshots in data/ folder for debugging.")
            print("The site may have changed structure or be blocking scrapers.")

        return 0
    else:
        print("\nScraping failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
