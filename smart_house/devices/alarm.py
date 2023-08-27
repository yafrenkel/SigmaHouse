# -*- coding: utf-8 -*-
"""Provides Alarm device class."""

from time import ticks_ms

from devices.device import Device

from machine import Timer


class Alarm(Device):
    """Implements Alarm class."""

    ALARM_MODE_NONE = 0
    ALARM_MODE_LOCAL = 1
    ALARM_MODE_GLOBAL = 2
    ALARM_MODE_SENSOR = 3

    def __init__(
        self,
        name="/dev/alarm",
        timer_num=-1,
        event_queue=None,
        debug=False,
    ):
        """Initiate object's internal state."""
        super().__init__(name=name, event_queue=event_queue, debug=debug)

        self._log("Initiating")
        self._state = {
            "triggered": False,
            "armed": False,
            "mode": Alarm.ALARM_MODE_NONE,
            "armed_timestamp": 0,
            "triggered_timestamp": 0,
            "disarmed_timestamp": 0,
        }

        self._log("Initiating timer")
        self._timer = Timer(timer_num)

    def arm(self, mode=ALARM_MODE_LOCAL):
        """Arm alarm system in specific mode."""
        self._log(f"Armed in mode {mode}")
        self._state.update(
            {
                "armed": True,
                "mode": mode,
                "armed_timestamp": ticks_ms(),
            }
        )

    def set_trigger(self, triggered=True, period_ms=0):
        """Set trigger state for specific time period."""
        state_log_msg = "Triggered" if triggered else "Untriggered"
        for_duration = f" for {period_ms} ms" if period_ms != 0 else ""
        self._log(f"{state_log_msg}{for_duration}")

        self._state.update(
            {
                "triggered": triggered,
                "triggered_timestamp": ticks_ms(),
            }
        )

        if period_ms != 0:
            self._timer.init(
                period=period_ms,
                mode=Timer.ONE_SHOT,
                callback=self._trigger_toggle_callback,
            )

        self._push_event_state()

    def disarm(self, mode=ALARM_MODE_LOCAL):
        """Arm alarm system in specific mode."""
        self._log("Disarmed")
        self._state.update(
            {
                "armed": False,
                "triggered": False,
                "disarmed_timestamp": ticks_ms(),
            }
        )

    def _trigger_toggle_callback(self, _):
        """Toggle trigger state based on timer callback."""
        self.set_trigger(not self._state["triggered"])

    def finalize(self):
        """Disable timer."""
        self._log("Disabling timer")
        self._timer.deinit()
