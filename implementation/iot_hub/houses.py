"""In-memory store of registered houses.

This module is the only place that reads or writes the HOUSES dict.
It has no Flask imports on purpose: app.py handles HTTP, this file
handles data. That makes it easy to test in a Python REPL.
"""

import time
from datetime import datetime, timedelta
from threading import Lock

from constants import LOST_AFTER_S, MOTION_HOLD_S, VALID_DEVICES

# {unique_id: house_record}. Lost on server restart -- devices re-register
# automatically on their next keepalive (which will get a 404 and trigger
# them to POST /api/houses again from the firmware).
HOUSES: dict[str, dict] = {}

# {unique_id: monotonic seconds of last motion report}. Kept OUT of the
# house record so the records stay JSON-clean for jsonify().
_MOTION_TS: dict[str, float] = {}

# One coarse lock around the whole dict. Flask's dev server can serve
# requests from multiple threads, so we need this to keep updates atomic.
_LOCK = Lock()


def now_str() -> str:
    """Current local time as 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _default_state() -> dict:
    return {
        "led": {"active": False},
        "fan": {"active": False, "clockwise": True},
        "buzzer": {"active": False},
        "motion": {"detected": False},
    }


def _expire_motion(house: dict) -> None:
    """Clear a house's 'Motion!' once MOTION_HOLD_S has passed since the report."""
    if not house["state"]["motion"]["detected"]:
        return
    ts = _MOTION_TS.get(house["unique_id"])
    if ts is not None and time.monotonic() - ts >= MOTION_HOLD_S:
        house["state"]["motion"]["detected"] = False


def list_all() -> list[dict]:
    """Return a snapshot of every house, for the dashboard."""
    with _LOCK:
        for house in HOUSES.values():
            _expire_motion(house)
        return list(HOUSES.values())


def register(unique_id: str, ip_address: str) -> dict:
    """Create or refresh a house record."""
    with _LOCK:
        HOUSES[unique_id] = {
            "unique_id": unique_id,
            "ip_address": ip_address,
            "status": "Active",
            "last_seen": now_str(),
            "alarm_armed": False,
            "alarm_triggered": False,
            "pending_state_update": False,
            "state": _default_state(),
        }
        return HOUSES[unique_id]


def keepalive(unique_id: str, ip_address: str) -> dict | None:
    """Mark the house as alive. Returns flags telling the device what to do.

    The 'alarm' flag is one-shot: returning True clears it, so the device
    only fires its buzzer once per motion event.
    """
    with _LOCK:
        house = HOUSES.get(unique_id)
        if house is None:
            return None
        house["last_seen"] = now_str()
        house["ip_address"] = ip_address
        house["status"] = "Active"
        alarm = house["alarm_triggered"]
        house["alarm_triggered"] = False
        return {"alarm": alarm, "state_update": house["pending_state_update"]}


def get_state(unique_id: str) -> dict | None:
    """Return the current desired state. Clears the pending flag."""
    with _LOCK:
        house = HOUSES.get(unique_id)
        if house is None:
            return None
        house["pending_state_update"] = False
        return house["state"]


def set_state(unique_id: str, state: dict) -> bool:
    """Device pushes its actual current state (after applying changes)."""
    with _LOCK:
        house = HOUSES.get(unique_id)
        if house is None:
            return False
        house["state"] = state
        return True


def toggle_device(unique_id: str, device: str) -> bool:
    """Flip the 'active' bit of led/fan/buzzer and signal a state update."""
    if device not in VALID_DEVICES:
        return False
    with _LOCK:
        house = HOUSES.get(unique_id)
        if house is None:
            return False
        house["state"][device]["active"] = not house["state"][device]["active"]
        house["pending_state_update"] = True
        return True


def arm_alarm(unique_id: str, armed: bool) -> bool:
    """Arm or disarm the alarm. Disarming also clears any active buzzer."""
    with _LOCK:
        house = HOUSES.get(unique_id)
        if house is None:
            return False
        house["alarm_armed"] = armed
        if not armed:
            house["alarm_triggered"] = False
            house["state"]["buzzer"]["active"] = False
            house["pending_state_update"] = True
        return True


def report_motion(unique_id: str) -> bool:
    """A device reports motion. If it's armed, fire all armed houses."""
    with _LOCK:
        reporter = HOUSES.get(unique_id)
        if reporter is None:
            return False
        reporter["state"]["motion"]["detected"] = True
        _MOTION_TS[unique_id] = time.monotonic()
        if not reporter["alarm_armed"]:
            return True
        for house in HOUSES.values():
            if house["alarm_armed"]:
                house["alarm_triggered"] = True
        return True


def delete(unique_id: str) -> bool:
    with _LOCK:
        _MOTION_TS.pop(unique_id, None)
        return HOUSES.pop(unique_id, None) is not None


def mark_lost_if_stale() -> None:
    """Watchdog: any active house with no recent keepalive becomes 'Lost'."""
    cutoff = datetime.now() - timedelta(seconds=LOST_AFTER_S)
    with _LOCK:
        for house in HOUSES.values():
            if house["status"] != "Active":
                continue
            last = datetime.strptime(house["last_seen"], "%Y-%m-%d %H:%M:%S")
            if last < cutoff:
                house["status"] = "Lost"
                house["alarm_armed"] = False
                house["alarm_triggered"] = False
                house["state"]["buzzer"]["active"] = False
