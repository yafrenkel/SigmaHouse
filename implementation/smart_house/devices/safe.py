"""Let the house run even if a peripheral isn't wired.

If a device fails to start up (loose wire, wrong I2C address, missing
part), we print a warning and use a harmless Stub instead of crashing the
whole program. So you can test with just an LED, and a wiggled cable at
camp won't take a whole house down.
"""


class Stub:
    """A do-nothing stand-in for a device that isn't available.

    It answers every method the firmware might call, with safe defaults,
    so the rest of the code never needs to check 'is this device real?'.
    """

    def on(self, *args, **kwargs):
        pass

    def off(self):
        pass

    def beep(self, *args, **kwargs):
        pass

    def is_on(self):
        return False

    def was_pressed(self):
        return False

    def was_triggered(self):
        return False

    def is_active(self):
        return False

    def show(self, *args, **kwargs):
        pass

    def state(self):
        return {"active": False, "clockwise": True, "detected": False}


def safe(make, name):
    """Build a device with make(); on ANY failure, warn and return a Stub."""
    try:
        return make()
    except Exception as e:
        print("WARNING:", name, "not available -", e, "- using stub")
        return Stub()
