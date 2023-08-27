"""Defines CRUD operations with house models."""
from datetime import datetime

from flask import abort, make_response


HOUSES = {
    "1337CAFEC0DE": {
        "unique_id": "1337CAFEC0DE",
        "ip_address": "192.168.1.42",
        "status": "Registered",
        "timestamp_keepalive": "2023-07-13 00:01:02",
        "timestamp_created": "2023-07-13 00:01:02",
        "timestamp_modified": "",
        "timestamp_deleted": "",
        "update_from_ui": False,
        "global_alarm": False,
        "state": {
            "alarm": {
                "triggered": False,
                "armed": False,
                "mode": 0,
                "armed_timestamp": 0,
                "triggered_timestamp": 0,
                "disarmed_timestamp": 0,
            },
            "buzzer": {
                "active": False,
                "timestamp": 0,
            },
            "fan": {
                "active": False,
                "clockwise": True,
                "timestamp": 0,
            },
            "led": {
                "active": False,
                "timestamp": 0,
            },
            "motion": {
                "motion_detected": False,
                "triggered_timestamp": 0,
                "released_timestamp": 0,
            },
            "wall_msg": "ID:1337CAFECODE",
        },
    },
    "1337C0FFFEEE": {
        "unique_id": "1337C0FFFEEE",
        "ip_address": "192.168.1.24",
        "status": "Registered",
        "timestamp_keepalive": "2023-07-13 00:01:02",
        "timestamp_created": "2023-07-13 00:01:02",
        "timestamp_modified": "",
        "timestamp_deleted": "",
        "update_from_ui": False,
        "global_alarm": False,
        "state": {
            "alarm": {
                "triggered": False,
                "armed": False,
                "mode": 0,
                "armed_timestamp": 0,
                "triggered_timestamp": 0,
                "disarmed_timestamp": 0,
            },
            "buzzer": {
                "active": False,
                "timestamp": 0,
            },
            "fan": {
                "active": False,
                "clockwise": True,
                "timestamp": 0,
            },
            "led": {
                "active": False,
                "timestamp": 0,
            },
            "motion": {
                "motion_detected": False,
                "triggered_timestamp": 0,
                "released_timestamp": 0,
            },
            "wall_msg": "ID:1337C0FFFEEE",
        },
    },
}


def get_timestamp():
    """Provide human-readable timestamp."""
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


def read_all():
    """Get the list of registered houses."""
    return list(HOUSES.values())


def create(house):
    """Register a new house with the IoT hub."""
    unique_id = house.get("unique_id")
    ip_address = house.get("ip_address", "")
    state = house.get("state")
    action_timestamp = get_timestamp()

    HOUSES[unique_id] = {
        "unique_id": unique_id,
        "ip_address": ip_address,
        "status": "Registered",
        "timestamp_keepalive": action_timestamp,
        "timestamp_created": action_timestamp,
        "timestamp_modified": "",
        "timestamp_deleted": "",
        "update_from_ui": False,
        "global_alarm": False,
        "state": state,
    }

    return make_response(
        {
            "message": "House registered successfully",
            "unique_id": unique_id,
        },
        201,
    )


def keepalive(unique_id, house):
    """Update keepalive timestamp of a house in IoT hub records."""
    ip_address = house.get("ip_address", "")

    if unique_id in HOUSES:
        HOUSES[unique_id].update(
            {
                "ip_address": ip_address,
                "status": "Active",
                "timestamp_keepalive": get_timestamp(),
            }
        )

        if HOUSES[unique_id]["global_alarm"]:
            HOUSES[unique_id]["global_alarm"] = False

            return make_response(
                {
                    "message": "Keepalive received, activate alarm now",
                    "unique_id": unique_id,
                },
                202,
            )

        if HOUSES[unique_id]["update_from_ui"]:
            return make_response(
                {
                    "message": "Keepalive received, state update available",
                    "unique_id": unique_id,
                },
                205,
            )

        else:
            return make_response(
                {
                    "message": "Keepalive received, no state update to report",
                    "unique_id": unique_id,
                },
                200,
            )

    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )


def delete(unique_id):
    """Delete a house from the IoT hub."""
    if unique_id in HOUSES:
        HOUSES[unique_id].update(
            {
                "status": "Deleted",
                "timestamp_deleted": get_timestamp(),
            }
        )

        return make_response(
            {
                "message": "House de-activated successfully",
                "unique_id": unique_id,
            },
            200,
        )
    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )


def get_state(unique_id):
    """Get house data from the IoT hub."""
    if unique_id in HOUSES and HOUSES[unique_id]["status"] != "Deleted":
        if HOUSES[unique_id]["update_from_ui"]:
            HOUSES[unique_id]["update_from_ui"] = False

        return make_response(
            HOUSES[unique_id]["state"],
            200,
        )
    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )


def set_state(unique_id, house):
    """Set house data in the IoT hub."""
    state = house.get("state")
    if unique_id in HOUSES:
        HOUSES[unique_id].update(
            {
                "state": state,
                "timestamp_modified": get_timestamp(),
            }
        )

        return make_response(
            {
                "message": "House state updated successfully",
                "unique_id": unique_id,
            },
            200,
        )
    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )


def toggle_device(unique_id, device):
    """Toggle device state for a house."""
    if unique_id in HOUSES:
        device_state = HOUSES[unique_id]["state"][device]["active"]
        HOUSES[unique_id]["state"][device]["active"] = not device_state
        HOUSES[unique_id]["state"][device]["timestamp"] = datetime.now().timestamp()

        HOUSES[unique_id].update(
            {
                "update_from_ui": True,
                "timestamp_modified": get_timestamp(),
            }
        )

        return make_response(
            {
                "message": f"Device {device.capitalize()} toggled successfully",
                "unique_id": unique_id,
            },
            200,
        )
    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )


def report_alarm(unique_id):
    """Receive alarm report for a house and trigger other global alarms."""
    if unique_id in HOUSES:
        if HOUSES[unique_id]["state"]["alarm"]["mode"] == 2:  # ALARM_MODE_GLOBAL
            for house in HOUSES:
                if (
                    house != unique_id and HOUSES[house]["state"]["alarm"]["mode"] == 2
                ):  # ALARM_MODE_GLOBAL
                    HOUSES[house].update(
                        {
                            "global_alarm": True,
                            "timestamp_modified": get_timestamp(),
                        }
                    )

        return make_response(
            {
                "message": "Alarm report processed successfully",
                "unique_id": unique_id,
            },
            200,
        )
    else:
        abort(
            404,
            {
                "message": "House not found",
                "unique_id": unique_id,
            },
        )
