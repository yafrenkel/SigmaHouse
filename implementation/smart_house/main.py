"""Entry point. MicroPython runs this automatically on boot.

Picks the firmware version based on USE_ASYNC in config.py.
Edit that flag to switch between the two implementations.
"""

import config

if config.USE_ASYNC:
    from app_async import run
else:
    from app_sync import run

run()
