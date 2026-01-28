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


def build_email_html(analysis):
    """Build the weekly update HTML email."""
    today = datetime.now().strftime('%B %d, %Y')

    # Extract key metrics from analysis data
    if analysis:
        incidents = analysis.get('incidents', [])
        trend = analysis.get('trend_analysis', {})
        total_incidents = len(incidents)
        latest = incidents[-1] if incidents else {}
        latest_mpi = latest.get('miles_between_incidents', 'N/A')
        if isinstance(latest_mpi, (int, float)):
            latest_mpi_fmt = f'{latest_mpi:,.0f}'
        else:
            latest_mpi_fmt = str(latest_mpi)

        doubling_time = trend.get('doubling_time_days', 'N/A')
        r_squared = trend.get('r_squared', 'N/A')
        if isinstance(r_squared, float):
            r_squared = f'{r_squared:.3f}'
        forecast = trend.get('forecast_30_day', 'N/A')
        if isinstance(forecast, (int, float)):
            forecast_fmt = f'{forecast:,.0f}'
        else:
            forecast_fmt = str(forecast)
    else:
        total_incidents = 'N/A'
        latest_mpi_fmt = 'N/A'
        doubling_time = 'N/A'
        r_squared = 'N/A'
        forecast_fmt = 'N/A'

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

    <!-- Metrics Card -->
    <div style="background:#161616; border:1px solid #27272a; border-radius:12px; padding:24px; margin-bottom:24px;">
      <h2 style="color:#ffffff; font-size:16px; margin:0 0 20px; text-align:center;">This Week's Safety Metrics</h2>
      <table style="width:100%; border-collapse:collapse;">
        <tr>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a;">
            <span style="color:#a1a1aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Latest Interval</span><br>
            <span style="color:#3b82f6; font-size:24px; font-weight:700;">{latest_mpi_fmt}</span>
            <span style="color:#71717a; font-size:13px;"> miles</span>
          </td>
          <td style="padding:12px 8px; border-bottom:1px solid #27272a; text-align:right;">
            <span style="color:#a1a1aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Total Incidents</span><br>
            <span style="color:#ffffff; font-size:24px; font-weight:700;">{total_incidents}</span>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 8px;">
            <span style="color:#a1a1aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">Doubling Time</span><br>
            <span style="color:#22c55e; font-size:20px; font-weight:600;">{doubling_time} days</span>
          </td>
          <td style="padding:12px 8px; text-align:right;">
            <span style="color:#a1a1aa; font-size:12px; text-transform:uppercase; letter-spacing:0.5px;">30-Day Forecast</span><br>
            <span style="color:#f59e0b; font-size:20px; font-weight:600;">{forecast_fmt}</span>
            <span style="color:#71717a; font-size:13px;"> mi</span>
          </td>
        </tr>
      </table>
    </div>

    <!-- Trend info -->
    <div style="background:#161616; border:1px solid #27272a; border-radius:12px; padding:20px; margin-bottom:24px;">
      <p style="color:#a1a1aa; font-size:14px; line-height:1.7; margin:0;">
        The best-fit model is <strong style="color:#ffffff;">exponential</strong> (R&sup2; = {r_squared}),
        meaning safety is doubling approximately every <strong style="color:#22c55e;">{doubling_time} days</strong>.
        At this rate, Tesla's robotaxi fleet is projected to reach
        <strong style="color:#f59e0b;">{forecast_fmt}</strong> miles per incident within 30 days.
      </p>
    </div>

    <!-- CTA -->
    <div style="text-align:center; margin-bottom:32px;">
      <a href="{TRACKER_URL}" style="display:inline-block; padding:12px 28px; background:#3b82f6; color:#ffffff; text-decoration:none; border-radius:8px; font-weight:600; font-size:14px;">
        View Live Dashboard
      </a>
    </div>

    <!-- Footer -->
    <div style="text-align:center; border-top:1px solid #27272a; padding-top:20px;">
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


def build_email_text(analysis):
    """Build plain-text fallback."""
    today = datetime.now().strftime('%B %d, %Y')
    lines = [
        f'Tesla Robotaxi Safety Tracker - Weekly Update ({today})',
        '=' * 55,
        '',
    ]
    if analysis:
        incidents = analysis.get('incidents', [])
        trend = analysis.get('trend_analysis', {})
        latest = incidents[-1] if incidents else {}
        latest_mpi = latest.get('miles_between_incidents', 'N/A')
        if isinstance(latest_mpi, (int, float)):
            latest_mpi = f'{latest_mpi:,.0f}'
        lines.append(f'Latest Interval: {latest_mpi} miles')
        lines.append(f'Total Incidents: {len(incidents)}')
        lines.append(f'Doubling Time: {trend.get("doubling_time_days", "N/A")} days')
        forecast = trend.get('forecast_30_day', 'N/A')
        if isinstance(forecast, (int, float)):
            forecast = f'{forecast:,.0f}'
        lines.append(f'30-Day Forecast: {forecast} miles/incident')
    else:
        lines.append('Analysis data not available. Visit the dashboard for the latest.')

    lines.extend([
        '',
        f'View the live dashboard: {TRACKER_URL}',
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

    # Build email content
    today = datetime.now().strftime('%b %d, %Y')
    subject = f'Robotaxi Safety Update - {today}'
    html = build_email_html(analysis)
    text = build_email_text(analysis)

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
