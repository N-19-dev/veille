#!/usr/bin/env python3
"""
Send push notification for new weekly digest.
Called after the weekly pipeline completes.
"""

import os
import sys
import requests
from datetime import datetime, timedelta

def get_current_week_label():
    """Get the current ISO week label (e.g., '2025w05')."""
    today = datetime.now()
    iso_calendar = today.isocalendar()
    return f"{iso_calendar[0]}w{iso_calendar[1]:02d}"

def send_weekly_digest_notification(week_label: str, title: str = None):
    """Send push notification to all users about new weekly digest."""

    # Firebase Cloud Function URL
    function_url = os.getenv("NOTIFICATION_FUNCTION_URL")
    api_key = os.getenv("NOTIFICATION_API_KEY")

    if not function_url or not api_key:
        print("Warning: NOTIFICATION_FUNCTION_URL or NOTIFICATION_API_KEY not set")
        print("Skipping push notification")
        return False

    try:
        response = requests.post(
            function_url,
            json={
                "weekLabel": week_label,
                "title": title or f"Le Top 3 de la semaine {week_label} est arrivé !"
            },
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Push notification sent: {result.get('sent', 0)}/{result.get('total', 0)} users")
            return True
        else:
            print(f"Error sending notification: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False

if __name__ == "__main__":
    week_label = sys.argv[1] if len(sys.argv) > 1 else get_current_week_label()
    send_weekly_digest_notification(week_label)
