#!/usr/bin/env python3
"""
Test SMTP connection to Hostinger email server.

Usage:
    # With .env file in project root:
    python scripts/test_smtp.py

    # With environment variables:
    SMTP_HOST=smtp.hostinger.com SMTP_PORT=465 \
    SMTP_USER=weekly-update@robotaxi-safety-tracker.com \
    SMTP_PASS=your-password python scripts/test_smtp.py

    # Send a test email to a specific address:
    python scripts/test_smtp.py --to your@email.com
"""
import os
import sys
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


def load_env():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def test_smtp(send_to=None):
    """Test SMTP connection and optionally send a test email."""
    load_env()

    host = os.environ.get('SMTP_HOST', 'smtp.hostinger.com')
    port = int(os.environ.get('SMTP_PORT', '465'))
    user = os.environ.get('SMTP_USER', '')
    password = os.environ.get('SMTP_PASS', '')

    if not user or not password:
        print('ERROR: SMTP_USER and SMTP_PASS must be set.')
        print('Create a .env file in the project root or set environment variables.')
        print('See .env.example for the template.')
        sys.exit(1)

    print(f'Testing SMTP connection to {host}:{port}...')

    try:
        server = smtplib.SMTP_SSL(host, port, timeout=30)
        print('  [OK] SSL connection established')

        server.login(user, password)
        print('  [OK] Login successful')

        if send_to:
            msg = MIMEMultipart('alternative')
            msg['From'] = f'Tesla Robotaxi Safety Tracker <{user}>'
            msg['To'] = send_to
            msg['Subject'] = 'Test - Weekly Update Subscription'

            text = (
                'This is a test email from the Tesla Robotaxi Safety Tracker.\n\n'
                'If you received this, the SMTP configuration is working correctly.\n\n'
                'Visit: https://kangning-huang.github.io/tesla_robotaxi_mile_per_incident_tracker/'
            )
            html = """\
<html>
<body style="font-family: 'Inter', Arial, sans-serif; background: #0a0a0a; color: #ffffff; padding: 40px;">
  <div style="max-width: 600px; margin: 0 auto; background: #161616; border: 1px solid #27272a; border-radius: 16px; padding: 32px;">
    <h2 style="color: #3b82f6; margin-top: 0;">SMTP Test Successful</h2>
    <p style="color: #a1a1aa;">This is a test email from the Tesla Robotaxi Safety Tracker subscription system.</p>
    <p style="color: #22c55e; font-weight: 600;">The email server is working correctly.</p>
    <hr style="border: none; border-top: 1px solid #27272a; margin: 24px 0;">
    <p style="color: #71717a; font-size: 13px;">
      <a href="https://kangning-huang.github.io/tesla_robotaxi_mile_per_incident_tracker/" style="color: #3b82f6;">
        Visit the Tracker
      </a>
    </p>
  </div>
</body>
</html>"""
            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            server.send_message(msg)
            print(f'  [OK] Test email sent to {send_to}')

        server.quit()
        print('  [OK] Connection closed')
        print('\nSMTP server is fully functional!')
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f'  [FAIL] Authentication failed: {e}')
        return False
    except smtplib.SMTPConnectError as e:
        print(f'  [FAIL] Connection failed: {e}')
        return False
    except Exception as e:
        print(f'  [FAIL] {type(e).__name__}: {e}')
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test SMTP connection')
    parser.add_argument('--to', help='Send a test email to this address')
    args = parser.parse_args()

    success = test_smtp(send_to=args.to)
    sys.exit(0 if success else 1)
