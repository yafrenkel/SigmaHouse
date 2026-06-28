"""Constants for the IoT hub. Edit here, not in app.py."""

# How often the watchdog checks for stale houses (seconds).
WATCHDOG_INTERVAL_S = 20

# A house is marked "Lost" if no keepalive arrives for this many seconds.
LOST_AFTER_S = 60

# Devices the dashboard is allowed to toggle.
VALID_DEVICES = ("led", "fan", "buzzer")

# How long the dashboard keeps showing "Motion!" after a report, before it
# auto-clears back to "No motion". Motion is an event (a pulse), so we hold
# the display for a few seconds rather than leaving it stuck on.
MOTION_HOLD_S = 3
