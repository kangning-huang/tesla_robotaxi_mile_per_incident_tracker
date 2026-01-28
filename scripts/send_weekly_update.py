#!/usr/bin/env python3
"""
Send weekly update emails to subscribers using Hostinger SMTP.

Reads analysis_results.json and subscribers.json, composes an HTML email
with the latest safety metrics, and sends it to all subscribers.

Usage:
    # With .env file:
    python scripts/send_weekly_update.py

    # Dry run (print email, don't send):
    python scripts/send_weekly_update.py --dry-run

    # Send to a single address (for testing):
    python scripts/send_weekly_update.py --test-to your@email.com
"""
import os
import sys
import json
import smtplib
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBSCRIBERS_PATH = PROJECT_ROOT / 'data' / 'subscribers.json'
ANALYSIS_PATH = PROJECT_ROOT / 'data' / 'analysis_results.json'
FLEET_DATA_PATH = PROJECT_ROOT / 'data' / 'fleet_data.json'
TRACKER_URL = 'https://kangning-huang.github.io/tesla_robotaxi_mile_per_incident_tracker/'


def load_env():
    """Load environment variables from .env file if it exists."""
    env_path = PROJECT_ROOT / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def load_subscribers():
    """Load subscriber emails from JSON file."""
    if not SUBSCRIBERS_PATH.exists():
        return []
    with open(SUBSCRIBERS_PATH) as f:
        data = json.load(f)
    return data.get('subscribers', [])


def load_analysis():
    """Load latest analysis results."""
    if not ANALYSIS_PATH.exists():
        return None
    with open(ANALYSIS_PATH) as f:
        return json.load(f)


def load_fleet_data():
    """Load latest fleet data."""
    if not FLEET_DATA_PATH.exists():
        return None
    with open(FLEET_DATA_PATH) as f:
        return json.load(f)


def _extract_metrics(analysis, fleet_data):
    """Extract and format all email metrics from analysis and fleet data."""
    metrics = {}

    if analysis:
        incidents = analysis.get('incidents', [])
        trend = analysis.get('trend_analysis', {})
        summary = analysis.get('summary', {})
        best_fit = trend.get('best_fit', {})
        exp_model = trend.get('all_models', {}).get('exponential', {})
        stoppages = analysis.get('service_stoppages', [])

        latest = incidents[-1] if incidents else {}
        metrics['total_incidents'] = len(incidents)
        metrics['latest_mpi_raw'] = latest.get('mpi_since_previous')
        metrics['cumulative_mpi_raw'] = summary.get('cumulative_mpi')
        metrics['total_miles_raw'] = summary.get('total_miles')
        metrics['latest_incident_date'] = latest.get('incident_date')
        metrics['service_start'] = analysis.get('service_start')
        metrics['analysis_date'] = analysis.get('analysis_date', '')[:10]

        # Trend info
        metrics['best_model'] = trend.get('best_model', 'N/A')
        metrics['r_squared_raw'] = best_fit.get('r_squared')
        metrics['current_trend'] = best_fit.get('current_trend', 'N/A')
        metrics['doubling_time_raw'] = exp_model.get('doubling_time_days')

        # Service stoppages
        metrics['stoppages'] = stoppages
    else:
        metrics['total_incidents'] = None

    if fleet_data:
        snapshots = fleet_data.get('snapshots', [])
        if snapshots:
            latest_snap = snapshots[-1]
            metrics['austin_vehicles'] = latest_snap.get('austin_vehicles')
            metrics['bayarea_vehicles'] = latest_snap.get('bayarea_vehicles')
            metrics['fleet_date'] = latest_snap.get('date')

    return metrics


def _fmt(value, fmt_str='{:,.0f}', fallback='N/A'):
    """Format a numeric value or return fallback."""
    if isinstance(value, (int, float)):
        return fmt_str.format(value)
    return fallback


def build_email_html(analysis, fleet_data=None):
    """Build the weekly update HTML email."""
    today = datetime.now().strftime('%B %d, %Y')
    m = _extract_metrics(analysis, fleet_data)

    latest_mpi = _fmt(m.get('latest_mpi_raw'))
    cumulative_mpi = _fmt(m.get('cumulative_mpi_raw'))
    total_miles = _fmt(m.get('total_miles_raw'))
    total_incidents = m.get('total_incidents', 'N/A')
    doubling_time = _fmt(m.get('doubling_time_raw'), '{:.0f}')
    r_squared = _fmt(m.get('r_squared_raw'), '{:.3f}')
    best_model = m.get('best_model', 'N/A')
    current_trend = m.get('current_trend', 'N/A')
    austin = m.get('austin_vehicles')
    bayarea = m.get('bayarea_vehicles')
    fleet_total = (austin or 0) + (bayarea or 0) if austin or bayarea else None

    # Fleet status line
    if austin is not None and bayarea is not None:
        fleet_line = f'{austin} Austin (autonomous) + {bayarea} Bay Area (w/ safety driver) = {fleet_total} total'
    else:
        fleet_line = None

    # Trend narrative
    if best_model != 'N/A' and doubling_time != 'N/A':
        trend_narrative = (
            f'The best-fit trend model is <strong style="color:#ffffff;">{best_model}</strong> '
            f'(R&sup2;&nbsp;=&nbsp;{r_squared}). '
            f'The exponential model estimates safety is doubling approximately every '
            f'<strong style="color:#22c55e;">{doubling_time}&nbsp;days</strong>.'
        )
    elif m.get('total_incidents') is not None:
        trend_narrative = 'Trend data is still being calculated. Check the dashboard for updates.'
    else:
        trend_narrative = 'Analysis data is not yet available.'

    # Current trend badge
    trend_color = '#22c55e' if current_trend == 'improving' else '#ef4444' if current_trend == 'worsening' else '#f59e0b'
    trend_label = current_trend.capitalize() if current_trend != 'N/A' else 'N/A'

    # Service stoppage note
    stoppage_html = ''
    stoppages = m.get('stoppages', [])
    if stoppages:
        reasons = [s.get('reason', 'Unknown') for s in stoppages]
        stoppage_html = f"""
    <div style="background:#1c1917; border:1px solid #44403c; border-radius:8px; padding:14px 16px; margin-bottom:24px;">
      <p style="color:#a8a29e; font-size:13px; margin:0;">
        &#9888;&#65039; <strong style="color:#fbbf24;">Service Note:</strong> {'; '.join(reasons)}.
        These dates are excluded from mileage calculations.
      </p>
    </div>"""

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background:#0a0a0a; font-family:'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px; margin:0 auto; padding:32px 20px;">

    <!-- Header -->
    <div style="text-align:center; margin-bottom:32px;">
      <h1 style="color:#3b82f6; font-size:22px; margin:0 0 4px;">Tesla Robotaxi Safety Tracker</h1>
      <p style="color:#71717a; font-size:13px; margin:0;">Weekly Update &mdash; {today}</p>
    </div>

    <!-- Key Metrics Card -->
    <div style="background:#161616; border:1px solid #27272a; border-radius:12px; padding:24px; margin-bottom:24px;">
      <h2 style="color:#ffffff; font-size:16px; margin:0 0 20px; text-align:center;">Safety Metrics</h2>
      <table style="width:100%; border-collapse:collapse;">
        <tr>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Latest Interval</span><br>
            <span style="color:#3b82f6; font-size:24px; font-weight:700;">{latest_mpi}</span>
            <span style="color:#71717a; font-size:13px;"> mi/incident</span>
          </td>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a; text-align:right;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Cumulative MPI</span><br>
            <span style="color:#8b5cf6; font-size:24px; font-weight:700;">{cumulative_mpi}</span>
            <span style="color:#71717a; font-size:13px;"> mi/incident</span>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Total Incidents</span><br>
            <span style="color:#ffffff; font-size:24px; font-weight:700;">{total_incidents}</span>
          </td>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a; text-align:right;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Total Miles Driven</span><br>
            <span style="color:#ffffff; font-size:24px; font-weight:700;">{total_miles}</span>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 8px;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Safety Doubling Time</span><br>
            <span style="color:#22c55e; font-size:20px; font-weight:600;">{doubling_time}</span>
            <span style="color:#71717a; font-size:13px;"> days</span>
          </td>
          <td style="padding:12px 8px; text-align:right;">
            <span style="color:#a1a1aa; font-size:11px; text-transform:uppercase; letter-spacing:0.5px;">Current Trend</span><br>
            <span style="color:{trend_color}; font-size:20px; font-weight:600;">{trend_label}</span>
          </td>
        </tr>
      </table>
    </div>

    <!-- Fleet Status -->
    {"" if not fleet_line else f'''<div style="background:#161616; border:1px solid #27272a; border-radius:12px; padding:20px; margin-bottom:24px;">
      <h3 style="color:#ffffff; font-size:14px; margin:0 0 10px;">Fleet Status</h3>
      <p style="color:#a1a1aa; font-size:14px; margin:0;">
        <strong style="color:#ffffff;">{fleet_total}</strong> vehicles &mdash; {fleet_line}
      </p>
    </div>'''}

    <!-- Trend Narrative -->
    <div style="background:#161616; border:1px solid #27272a; border-radius:12px; padding:20px; margin-bottom:24px;">
      <p style="color:#a1a1aa; font-size:14px; line-height:1.7; margin:0;">
        {trend_narrative}
      </p>
    </div>
{stoppage_html}
    <!-- CTA -->
    <div style="text-align:center; margin-bottom:32px;">
      <a href="{TRACKER_URL}" style="display:inline-block; padding:12px 28px; background:#3b82f6; color:#ffffff; text-decoration:none; border-radius:8px; font-weight:600; font-size:14px;">
        View Live Dashboard
      </a>
    </div>

    <!-- Footer -->
    <div style="text-align:center; border-top:1px solid #27272a; padding-top:20px;">
      <p style="color:#52525b; font-size:11px; margin:0 0 8px;">
        Data sourced from NHTSA SGO reports &amp; robotaxitracker.com. Updated {m.get('analysis_date', 'recently')}.
      </p>
      <p style="color:#71717a; font-size:12px; margin:0 0 8px;">
        You received this because you subscribed to Tesla Robotaxi Safety Tracker updates.
      </p>
      <p style="color:#71717a; font-size:12px; margin:0;">
        <a href="mailto:weekly-update@robotaxi-safety-tracker.com?subject=Unsubscribe&body=Please%20remove%20me%20from%20the%20weekly%20update%20list." style="color:#3b82f6; text-decoration:underline;">Unsubscribe</a>
        &nbsp;&bull;&nbsp;
        <a href="{TRACKER_URL}" style="color:#3b82f6; text-decoration:underline;">Visit Tracker</a>
      </p>
    </div>
  </div>
</body>
</html>"""


def build_email_text(analysis, fleet_data=None):
    """Build plain-text fallback."""
    today = datetime.now().strftime('%B %d, %Y')
    m = _extract_metrics(analysis, fleet_data)

    lines = [
        f'Tesla Robotaxi Safety Tracker - Weekly Update ({today})',
        '=' * 55,
        '',
    ]
    if m.get('total_incidents') is not None:
        lines.append(f'Latest Interval:    {_fmt(m.get("latest_mpi_raw"))} miles/incident')
        lines.append(f'Cumulative MPI:     {_fmt(m.get("cumulative_mpi_raw"))} miles/incident')
        lines.append(f'Total Incidents:    {m["total_incidents"]}')
        lines.append(f'Total Miles Driven: {_fmt(m.get("total_miles_raw"))}')
        lines.append(f'Safety Doubling:    ~{_fmt(m.get("doubling_time_raw"), "{:.0f}")} days')
        lines.append(f'Current Trend:      {m.get("current_trend", "N/A").capitalize()}')

        austin = m.get('austin_vehicles')
        bayarea = m.get('bayarea_vehicles')
        if austin is not None and bayarea is not None:
            lines.append('')
            lines.append(f'Fleet: {austin} Austin (autonomous) + {bayarea} Bay Area (safety driver) = {austin + bayarea} total')

        stoppages = m.get('stoppages', [])
        if stoppages:
            lines.append('')
            for s in stoppages:
                lines.append(f'Service Note: {s.get("reason", "N/A")}')
    else:
        lines.append('Analysis data not available. Visit the dashboard for the latest.')

    lines.extend([
        '',
        f'View the live dashboard: {TRACKER_URL}',
        '',
        f'Data sourced from NHTSA SGO reports & robotaxitracker.com.',
        '',
        '---',
        'Unsubscribe: Reply to this email with "Unsubscribe" in the subject.',
    ])
    return '\n'.join(lines)


def send_email(to_address, subject, html, text, smtp_config):
    """Send a single email."""
    msg = MIMEMultipart('alternative')
    msg['From'] = f'Tesla Robotaxi Safety Tracker <{smtp_config["user"]}>'
    msg['To'] = to_address
    msg['Subject'] = subject
    msg['List-Unsubscribe'] = f'<mailto:{smtp_config["user"]}?subject=Unsubscribe>'

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=30)
    server.login(smtp_config['user'], smtp_config['password'])
    server.send_message(msg)
    server.quit()


def main():
    parser = argparse.ArgumentParser(description='Send weekly update emails')
    parser.add_argument('--dry-run', action='store_true', help='Print email without sending')
    parser.add_argument('--test-to', help='Send only to this address (for testing)')
    args = parser.parse_args()

    load_env()

    smtp_config = {
        'host': os.environ.get('SMTP_HOST', 'smtp.hostinger.com'),
        'port': int(os.environ.get('SMTP_PORT', '465')),
        'user': os.environ.get('SMTP_USER', ''),
        'password': os.environ.get('SMTP_PASS', ''),
    }

    if not args.dry_run and (not smtp_config['user'] or not smtp_config['password']):
        print('ERROR: SMTP_USER and SMTP_PASS must be set.')
        sys.exit(1)

    # Load data
    analysis = load_analysis()
    if not analysis:
        print('WARNING: No analysis_results.json found. Email will have limited data.')
    fleet_data = load_fleet_data()

    # Build email content
    today = datetime.now().strftime('%b %d, %Y')
    subject = f'Robotaxi Safety Update - {today}'
    html = build_email_html(analysis, fleet_data)
    text = build_email_text(analysis, fleet_data)

    if args.dry_run:
        print('=== DRY RUN ===')
        print(f'Subject: {subject}')
        print(f'From: {smtp_config["user"]}')
        print()
        print(text)
        print()
        print(f'(HTML version: {len(html)} chars)')
        return

    # Determine recipients
    if args.test_to:
        recipients = [args.test_to]
        print(f'Test mode: sending to {args.test_to}')
    else:
        recipients = load_subscribers()
        if not recipients:
            print('No subscribers found in data/subscribers.json')
            return

    # Send emails
    sent = 0
    failed = 0
    for email_addr in recipients:
        try:
            send_email(email_addr, subject, html, text, smtp_config)
            sent += 1
            print(f'  Sent to {email_addr}')
        except Exception as e:
            failed += 1
            print(f'  FAILED for {email_addr}: {e}')

    print(f'\nDone: {sent} sent, {failed} failed out of {len(recipients)} recipients.')


if __name__ == '__main__':
    main()
