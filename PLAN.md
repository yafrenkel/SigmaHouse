# Sigma Camp IoT — Clean Rewrite Plan

## Context[day1.md](tutorial/day1.md)
The existing `SigmaHouse-master/` project teaches summer-camp students about IoT using a Keyestudio ESP32 Smart Home kit, but the code has accreted complexity that's hard for 14-year-olds with basic Python: Connexion + OpenAPI on the hub, uasyncio + event queues + `micropython.schedule` chaining + a 4-mode alarm + a buggy half-finished RFID stack on the firmware, plus several scratch/hello files. The camp runs offline (intranet only), so all dependencies must be downloaded once before camp.

The rewrite, living at `C:/Projects/sigma/claude/`, will:
- Drop Connexion/OpenAPI [day1.md](tutorial/day1.md)
[day2.md](tutorial/day2.md)
[day3.md](tutorial/day3.md)
[day4.md](tutorial/day4.md)
[day5.md](tutorial/day5.md)
[INDEX.md](tutorial/INDEX.md)in favor of plain Flask routes a student can read top-to-bottom.
- Drop RFID, the 4-mode alarm, the wall message, and dead/scratch files.
- Keep only the peripherals actually used: LED, two Buttons, PIR motion, Fan, Buzzer, LCD1602 I2C.
- Provide BOTH a synchronous-loop firmware (default, beginner path) and an `uasyncio` firmware (advanced students), selected by a `USE_ASYNC` flag in `config.py`. Both share the same device drivers and HTTP client.
- Replace the original's 202/205 status-code signaling with explicit JSON booleans (`{alarm, state_update}`) — easier to debug with curl.
- Stay in-memory only on the hub (no DB / no file persistence).
- Document a step-by-step pre-camp offline setup (pip wheels + MicroPython firmware + flashing).

The original `SigmaHouse-master/` stays untouched as reference material.

---

## Folder structure

```
C:/Projects/sigma/claude/
├── README.md                       # Top-level overview + pre-camp offline setup guide
├── PLAN.md                         # this file
├── tutorial/                       # 5-day curriculum + counsellor guide + slides
└── implementation/
    ├── iot_hub/
    │   ├── app.py                  # Flask routes + watchdog wiring (thin)
    │   ├── houses.py               # In-memory dict + pure data helpers (no Flask imports)
    │   ├── constants.py            # WATCHDOG_INTERVAL_S, LOST_AFTER_S, VALID_DEVICES
    │   ├── requirements.txt        # Flask only (pinned)
    │   ├── templates/
    │   │   └── index.html          # Single dashboard page
    │   └── static/
    │       ├── dashboard.js        # Polls /api/houses every 1s, click handlers
    │       └── style.css           # Table + status colors
    └── smart_house/
        ├── README.md               # Flashing + uploading firmware notes
        ├── main.py                 # Reads USE_ASYNC, dispatches to app_sync or app_async
        ├── config.py               # Pin numbers, hub URL via secrets, timing, USE_ASYNC
        ├── secrets_example.py      # Template — copy to secrets.py with WiFi creds
        ├── hub_client.py           # urequests wrapper: register/keepalive/push/get/report/delete
        ├── app_sync.py             # while-True loop using IRQ flags + time.sleep (DEFAULT)
        ├── app_async.py            # uasyncio version with create_task per concern (ADVANCED)
        ├── lcd_api.py              # Vendor HD44780 API (copied verbatim)
        ├── lcd_i2c.py              # Vendor PCF8574 driver (copied verbatim)
        └── devices/
            ├── __init__.py         # empty
            ├── led.py              # LED on/off (GPIO 12)
            ├── button.py           # Button with IRQ + flag (GPIO 25/26)
            ├── motion.py           # PIR with IRQ + flag (GPIO 13)
            ├── fan.py              # Dual H-bridge PWM (GPIO 18/19)
            ├── buzzer.py           # Single-tone PWM (GPIO 4)
            └── lcd.py              # Thin facade over lcd_i2c
```

---

## iot_hub design (plain Flask)

### `houses.py` — pure data layer (~120 lines)

Module-level `HOUSES = {}`. Record shape:

```python
{
  "unique_id": "AABBCCDDEEFF",
  "ip_address": "192.168.1.42",
  "status": "Active" | "Lost",                # DELETE removes the key, no "Deleted" state
  "last_seen": "2026-05-03 12:34:56",
  "alarm_armed": False,
  "alarm_triggered": False,                   # one-shot flag consumed by next keepalive
  "pending_state_update": False,              # set when dashboard toggles something
  "state": {
    "led":     {"active": False},
    "fan":     {"active": False, "clockwise": True},
    "buzzer":  {"active": False},
    "motion":  {"detected": False},
  }
}
```

Functions (all pure — return dicts or booleans, never call Flask):
- `now_str()` — timestamp string.
- `register(unique_id, ip)` — create record with default state.
- `keepalive(unique_id, ip)` — update `last_seen`, set `status="Active"`, return `{"alarm": bool, "state_update": bool}`, clear `alarm_triggered` (one-shot consumption).
- `get_state(unique_id)` — return `state` dict, clear `pending_state_update`.
- `set_state(unique_id, state)` — device pushes its ground-truth state.
- `toggle_device(unique_id, device)` — flip `state[device]["active"]`, set `pending_state_update=True`.
- `arm_alarm(unique_id, armed)` — set `alarm_armed`. If disarming, also clear `alarm_triggered` and `state.buzzer.active`.
- `report_motion(unique_id)` — if reporter is armed, set `alarm_triggered=True` on every armed house (the global-fire rule).
- `delete(unique_id)` — `HOUSES.pop(unique_id, None)`.
- `mark_lost_if_stale()` — iterate; for each house with `now - last_seen > LOST_AFTER_S` and `status=="Active"`, set `status="Lost"` and clear alarm/buzzer state.

### `constants.py`

```python
WATCHDOG_INTERVAL_S = 20
LOST_AFTER_S = 60
VALID_DEVICES = ("led", "fan", "buzzer")
```

### `app.py` — Flask routes (~110 lines)

Imports: `flask`, `threading`, `houses`, `constants`. **No Connexion. No APScheduler.**

**Watchdog**: self-re-arming `threading.Timer` (started under `if __name__ == "__main__":`, daemon=True). ~6 lines, no extra dependency.

**Routes (all return JSON except `/`):**

| Method | Path | Body in | Body out | Status |
|---|---|---|---|---|
| GET | `/` | — | renders `index.html` | 200 |
| GET | `/api/houses` | — | `[house, ...]` | 200 |
| POST | `/api/houses` | `{unique_id, ip_address}` | `{ok, unique_id}` | 201 |
| PUT | `/api/houses/<uid>/keepalive` | `{ip_address}` | `{alarm, state_update}` | 200 |
| GET | `/api/houses/<uid>/state` | — | the `state` dict | 200/404 |
| PUT | `/api/houses/<uid>/state` | `{state: {...}}` | `{ok}` | 200/404 |
| POST | `/api/houses/<uid>/toggle/<device>` | — | `{ok}` | 200/404 |
| POST | `/api/houses/<uid>/arm` | `{armed: bool}` | `{ok}` | 200/404 |
| POST | `/api/houses/<uid>/report_motion` | — | `{ok}` | 200/404 |
| DELETE | `/api/houses/<uid>` | — | `{ok}` | 200/404 |

Default port: **8080** (port 80 needs admin on Windows). README documents how to override.

### Data flow: motion → buzzer
1. Device PIR fires → `POST /api/houses/<uid>/report_motion`.
2. `houses.report_motion(uid)` flips `alarm_triggered=True` on every armed house.
3. On any armed device's next keepalive, hub returns `{"alarm": true, ...}` and clears its `alarm_triggered` (one-shot).
4. Device receives `alarm:true` → calls `buzzer.on()` locally.
5. Disarming via dashboard clears `alarm_triggered` + `state.buzzer.active`; devices see this on next state pull.

### Frontend
- `templates/index.html` (~50 lines): one `<table id="houses">` with empty `<tbody>` rebuilt by JS each second. Loads `dashboard.js` and `style.css`.
- `static/dashboard.js` (~80 lines): `setInterval(refresh, 1000)`; `fetch('/api/houses')`; rebuilds rows; click handlers on toggle/arm buttons hit `POST /api/houses/<uid>/toggle/<device>` and `POST /api/houses/<uid>/arm`.
- `static/style.css` (~30 lines): table borders, three status background colors (green=ok, yellow=armed, red=lost/triggered/motion), button styling. No frameworks.

### `requirements.txt`
```
Flask==3.0.3
```

---

## smart_house design (MicroPython)

### `config.py`
```python
from secrets import WIFI_SSID, WIFI_PASS, HUB_URL

USE_ASYNC = False                 # True for advanced students.
UPDATE_INTERVAL_MS = 1000

PIN_LED      = 12
PIN_BUTTON_A = 26
PIN_BUTTON_B = 25
PIN_PIR      = 13
PIN_FAN_A    = 18
PIN_FAN_B    = 19
PIN_BUZZER   = 4
PIN_I2C_SCL  = 22
PIN_I2C_SDA  = 21
LCD_I2C_ADDR = 0x27
LCD_ROWS     = 2
LCD_COLS     = 16

WIFI_TIMEOUT_S = 10
```

### `secrets_example.py` (copy to `secrets.py`, never committed)
```python
WIFI_SSID = "your-wifi"
WIFI_PASS = "your-pass"
HUB_URL   = "http://192.168.1.10:8080"
```

### `devices/` — each file 30–60 lines, **no inheritance**
- `led.py`: wraps `Pin(num, OUT)`. `on()`, `off()`, `is_on()`, `state()` → `{"active": bool}`.
- `button.py`: `Pin(num, IN, PULL_UP)` + IRQ. Handler is 3 lines: sets `self._pressed=True` if value==0. Public `was_pressed()` returns and clears the flag (edge-consume). No `micropython.schedule`, no event queue.
- `motion.py`: same pattern as button. `was_triggered()` returns/clears; `is_active()` reads pin directly for state reporting.
- `fan.py`: two `PWM(Pin(num))`. `on(clockwise=True)` sets one duty=512 the other 0. `off()` zeroes both. `state()` → `{"active": bool, "clockwise": bool}`.
- `buzzer.py`: single `PWM(Pin(num))`. `on()` sets `freq=2000, duty=512`; `off()` sets `duty=0`. **No melody/tone constants** — replaces ~90 lines of original with ~5. Optional `beep(ms=200)` for fun.
- `lcd.py`: facade over `lcd_i2c.I2cLcd`. Exposes `show(line1, line2="")`. Hides SoftI2C boilerplate.

### `hub_client.py` (~80 lines)
One `HubClient` class taking `hub_url` and `unique_id`. Methods, each a thin `urequests` call returning a dict (or `None` on error):
- `register(ip)` → `POST /api/houses`
- `keepalive(ip)` → `PUT .../keepalive`, returns `{alarm, state_update}`
- `get_state()` → `GET .../state`
- `push_state(state)` → `PUT .../state`
- `report_motion()` → `POST .../report_motion`
- `deregister()` → `DELETE .../<uid>`

Every call wraps `urequests.request(...)` in try/except, prints errors, **always closes the response** (sockets leak in MicroPython otherwise). This is the single networking surface — both `app_sync` and `app_async` import and use it identically. Note that urequests is blocking even from async code; the ~100–200ms stall is documented as a known limitation.

### `app_sync.py` (~120 lines) — DEFAULT teaching path
```python
def run():
    # 1. Connect WiFi (~15-line helper local to file)
    # 2. Build devices: LED, Button A, Button B, Motion, Fan, Buzzer, LCD
    # 3. lcd.show("Connecting...", ip)
    # 4. hub = HubClient(HUB_URL, unique_id())
    # 5. hub.register(ip); lcd.show("Ready", ip)
    # 6. menu_index = 0  (LED / FAN / BUZZER selectable with button A)
    # 7. last_keepalive = ticks_ms()
    #
    # while True:
    #     if button_a.was_pressed():
    #         menu_index = (menu_index + 1) % 3
    #         lcd.show("Select:", MENU[menu_index])
    #     if button_b.was_pressed():
    #         <toggle the currently-selected device locally>
    #         hub.push_state(build_state())
    #     if motion.was_triggered():
    #         hub.report_motion()
    #     if ticks_diff(ticks_ms(), last_keepalive) >= UPDATE_INTERVAL_MS:
    #         last_keepalive = ticks_ms()
    #         resp = hub.keepalive(ip)
    #         if resp:
    #             if resp["alarm"]: buzzer.on()
    #             if resp["state_update"]: apply_state(hub.get_state())
    #     time.sleep_ms(50)
```
Helpers: `build_state()` collects each device's `state()` into the wire format; `apply_state(s)` dispatches to `led/fan/buzzer` only when the value differs from current (avoids gratuitous PWM resets). 50 ms tick is fine: button presses >100 ms, motion pulses >1 s, keepalive 1 s.

### `app_async.py` (~150 lines) — ADVANCED path
Same logical structure as four `uasyncio` tasks sharing the same device objects + `HubClient`:
- `task_buttons()` — polls `was_pressed()` flags every 30 ms, toggles + push_state.
- `task_motion()` — polls `was_triggered()` every 50 ms; on True calls `hub.report_motion()`.
- `task_keepalive()` — `await sleep_ms(UPDATE_INTERVAL_MS)`; sends keepalive, handles `alarm`/`state_update`.
- `task_lcd()` — refreshes LCD on menu changes (signaled by an `asyncio.Event` set by buttons task).

```python
async def _amain():
    # setup devices, wifi, hub.register(ip)
    asyncio.create_task(task_buttons())
    asyncio.create_task(task_motion())
    asyncio.create_task(task_keepalive())
    asyncio.create_task(task_lcd())
    while True:
        await asyncio.sleep(3600)

def run():
    asyncio.run(_amain())
```

**Same device classes, same `hub_client`, same wire protocol.** Only task structure differs — students can diff the two files to learn what `async` actually changes.

### `main.py`
```python
from config import USE_ASYNC
if USE_ASYNC:
    from app_async import run
else:
    from app_sync import run
run()
```

---

## Pre-camp offline setup guide (in `claude/README.md`)

Step-by-step the user runs **once on a laptop with internet, before camp**. Substitute the latest MicroPython release at execution time.

```bash
# 0. Prereqs: Python 3.11+, git, USB stick / shared folder.

# 1. Clone repo onto the USB stick:
cd /path/to/usb
git clone <repo-url> sigma-camp

# 2. Pre-download Flask + flashing tools as wheels:
cd sigma-camp/claude/implementation/iot_hub
mkdir wheels
pip download -d wheels -r requirements.txt
pip download -d wheels esptool==4.7.0 mpremote==1.22.0

# 3. Download MicroPython firmware for ESP32 (verify URL/version before camp):
mkdir -p ../smart_house/firmware
curl -L -o ../smart_house/firmware/ESP32_GENERIC-v1.23.0.bin \
     https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin

# 4. Verify the wheels work offline-style on this same laptop:
python -m venv .venv
source .venv/Scripts/activate     # Windows bash; on cmd use .venv\Scripts\activate
pip install --no-index --find-links wheels -r requirements.txt
pip install --no-index --find-links wheels esptool mpremote

# 5. Flash one ESP32 to verify the firmware (replace COM5):
esptool.py --port COM5 erase_flash
esptool.py --port COM5 --baud 460800 write_flash -z 0x1000 \
    ../smart_house/firmware/ESP32_GENERIC-v1.23.0.bin

# 6. Upload firmware files (lcd_api.py + lcd_i2c.py REQUIRED):
cd ../smart_house
mpremote connect COM5 fs cp lcd_api.py :lcd_api.py
mpremote connect COM5 fs cp lcd_i2c.py :lcd_i2c.py
mpremote connect COM5 fs cp config.py :config.py
mpremote connect COM5 fs cp secrets.py :secrets.py
mpremote connect COM5 fs cp hub_client.py :hub_client.py
mpremote connect COM5 fs cp app_sync.py :app_sync.py
mpremote connect COM5 fs cp app_async.py :app_async.py
mpremote connect COM5 fs cp main.py :main.py
mpremote connect COM5 fs mkdir devices
mpremote connect COM5 fs cp devices/*.py :devices/

# 7. Boot it: mpremote connect COM5 repl  (Ctrl-D soft-reset; LCD shows "Connecting...")

# === At camp, no internet — each student laptop ===
cd <usb>/sigma-camp/claude/implementation/iot_hub
python -m venv .venv && source .venv/Scripts/activate
pip install --no-index --find-links wheels -r requirements.txt
pip install --no-index --find-links wheels esptool mpremote
python app.py    # http://<laptop-ip>:8080  — find IP via ipconfig
```

Note: hub runs on **port 8080** by default to avoid Windows admin requirement. Students set `HUB_URL = "http://<laptop-ip>:8080"` in `secrets.py`.

---

## What's removed from the original

| Removed | Reason |
|---|---|
| `connexion` + `openapi.yaml` | Heavy dep + spec layer; five Flask routes don't need a contract. |
| `Flask-APScheduler` / `apscheduler` | One self-re-arming `threading.Timer` replaces it. |
| HTTP 202/205 control-flow signaling | Replaced by explicit JSON booleans `{alarm, state_update}`. |
| 4-mode alarm (none/local/global/sensor) | Reduced to one global mode. |
| `wall_msg` field + LCD push from hub | LCD shows local menu/state instead. |
| Whole RFID stack (`mfrc522_*.py`, `rfid_lock.py`, `soft_iic.py`, `pj10_*.py`, `rfid_hello*.py`, `ui_index_rfid.html`) | Buggy and out of scope. |
| `hello*.py`, `xyz.py`, `app_org.py`, `main_hello_server.py`, `main_wifi.py`, `detect_i2c.py` | Dead/scratch files. |
| `templates/hello_world.html`, `templates/list_houses.html` | Single `index.html` covers it. |
| `core/menu.py` (TextMenu) | Inlined as a 3-item list + index in `app_sync.py`. |
| `devices/device.py` base class | Each device is standalone — simpler for 14-year-olds. |
| `event_queue` + `micropython.schedule` chaining | Replaced with simple boolean flags consumed in the loop. |
| Buzzer melody + ~80 tone constants | Replaced by `freq=2000, duty=512`. |
| `pyproject.toml`, `poetry.lock` | Plain `requirements.txt`. |

---

## Critical files to be created

- [README.md](claude/README.md) — overview + offline setup guide
- [iot_hub/app.py](claude/implementation/iot_hub/app.py) — Flask routes (~110 lines)
- [iot_hub/houses.py](claude/implementation/iot_hub/houses.py) — data layer (~120 lines)
- [iot_hub/constants.py](claude/implementation/iot_hub/constants.py) — magic numbers
- [iot_hub/requirements.txt](claude/implementation/iot_hub/requirements.txt) — `Flask==3.0.3`
- [iot_hub/templates/index.html](claude/implementation/iot_hub/templates/index.html) — dashboard
- [iot_hub/static/dashboard.js](claude/implementation/iot_hub/static/dashboard.js) — polling + click handlers
- [iot_hub/static/style.css](claude/implementation/iot_hub/static/style.css) — colors
- [smart_house/main.py](claude/implementation/smart_house/main.py) — dispatch on USE_ASYNC
- [smart_house/config.py](claude/implementation/smart_house/config.py) — pins + flags
- [smart_house/secrets_example.py](claude/implementation/smart_house/secrets_example.py) — template
- [smart_house/hub_client.py](claude/implementation/smart_house/hub_client.py) — urequests wrapper
- [smart_house/app_sync.py](claude/implementation/smart_house/app_sync.py) — sync loop (default)
- [smart_house/app_async.py](claude/implementation/smart_house/app_async.py) — uasyncio version
- [smart_house/lcd_api.py](claude/implementation/smart_house/lcd_api.py) — vendor (copy verbatim)
- [smart_house/lcd_i2c.py](claude/implementation/smart_house/lcd_i2c.py) — vendor (copy verbatim)
- [smart_house/devices/led.py](claude/implementation/smart_house/devices/led.py)
- [smart_house/devices/button.py](claude/implementation/smart_house/devices/button.py)
- [smart_house/devices/motion.py](claude/implementation/smart_house/devices/motion.py)
- [smart_house/devices/fan.py](claude/implementation/smart_house/devices/fan.py)
- [smart_house/devices/buzzer.py](claude/implementation/smart_house/devices/buzzer.py)
- [smart_house/devices/lcd.py](claude/implementation/smart_house/devices/lcd.py)
- [smart_house/devices/__init__.py](claude/implementation/smart_house/devices/__init__.py) — empty

Vendor files copied verbatim from `SigmaHouse-master/smart_house/devices/lcd_api.py` and `lcd_i2c.py`.

## File-size targets

| File | Target | Hard cap |
|---|---|---|
| `iot_hub/app.py` | ~110 | 150 |
| `iot_hub/houses.py` | ~120 | 150 |
| `iot_hub/constants.py` | ~10 | 20 |
| `iot_hub/templates/index.html` | ~50 | 80 |
| `iot_hub/static/dashboard.js` | ~80 | 120 |
| `iot_hub/static/style.css` | ~30 | 60 |
| `smart_house/main.py` | ~15 | 25 |
| `smart_house/config.py` | ~30 | 50 |
| `smart_house/hub_client.py` | ~80 | 120 |
| `smart_house/app_sync.py` | ~120 | 150 |
| `smart_house/app_async.py` | ~150 | 180 |
| `smart_house/devices/*.py` | ~30–50 each | 70 |

Style: top-of-file docstring, type hints in CPython hub code (MicroPython files stay untyped), one blank line between methods, plain `for` loops over clever comprehensions.

---

## Verification plan

### 1. Hub alone (no ESP32)
Run `python claude/implementation/iot_hub/app.py`; open `http://localhost:8080/` (empty table). Then:
```bash
# Register fake house
curl -X POST http://localhost:8080/api/houses \
  -H "Content-Type: application/json" \
  -d '{"unique_id":"AABBCC112233","ip_address":"127.0.0.1"}'

# Keepalive
curl -X PUT http://localhost:8080/api/houses/AABBCC112233/keepalive \
  -H "Content-Type: application/json" -d '{"ip_address":"127.0.0.1"}'
# expect: {"alarm": false, "state_update": false}

# Toggle LED, then keepalive should report state_update
curl -X POST http://localhost:8080/api/houses/AABBCC112233/toggle/led
curl -X PUT http://localhost:8080/api/houses/AABBCC112233/keepalive \
  -H "Content-Type: application/json" -d '{"ip_address":"127.0.0.1"}'
curl http://localhost:8080/api/houses/AABBCC112233/state

# Arm + simulate motion
curl -X POST http://localhost:8080/api/houses/AABBCC112233/arm \
  -H "Content-Type: application/json" -d '{"armed":true}'
curl -X POST http://localhost:8080/api/houses/AABBCC112233/report_motion
curl -X PUT http://localhost:8080/api/houses/AABBCC112233/keepalive \
  -H "Content-Type: application/json" -d '{"ip_address":"127.0.0.1"}'
# expect: {"alarm": true, "state_update": false}

# Watchdog: stop sending keepalives, wait ~60s, refresh dashboard → status "Lost".
curl -X DELETE http://localhost:8080/api/houses/AABBCC112233
```

### 2. Two fake houses → motion propagation
Register two uids, arm both, `report_motion` on one, then keepalive on the OTHER → expect `{"alarm": true}`. Confirms global-fire rule.

### 3. Real ESP32 against laptop hub
1. Set `HUB_URL = "http://<laptop-ip>:8080"` in `secrets.py`.
2. Allow inbound 8080 in laptop firewall.
3. Power-cycle ESP32 → LCD shows "Connecting..." then "Ready".
4. Refresh dashboard → row appears with the board's MAC as `unique_id`.
5. Click LED button on dashboard → physical LED on within ~1 s.
6. Wave hand at PIR (alarm armed) → buzzer fires within ~1 s.
7. Repeat with `USE_ASYNC = True` — same observable behavior.

### 4. Pre-camp smoke checklist
- Watchdog marks `Lost` after ~60 s with no keepalive.
- Disarming clears `alarm_triggered` AND turns the buzzer off on next state pull.
- DELETE removes the row from the dashboard within 1 s.
- Two browsers open to the dashboard stay in sync.
- Offline install (`pip install --no-index --find-links wheels ...`) succeeds on a freshly-imaged laptop with airplane mode on.
