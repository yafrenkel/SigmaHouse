# Sigma Camp IoT — Smart Houses

Clean rewrite of the SigmaHouse summer-camp project, simplified for 14-year-olds with some Python experience.

Two parts:

- **`iot_hub/`** — Flask web server. Runs on a counsellor's laptop. Shows a dashboard listing every connected house and lets you toggle their devices.
- **`smart_house/`** — MicroPython firmware for the ESP32 (Keyestudio Smart Home kit). Each board polls the hub, reports its state, and obeys commands sent from the dashboard.

Communication is plain HTTP REST. Everything must work **without internet** during camp — only the local WiFi router.

## How they talk to each other

```
ESP32 boards                     Counsellor's laptop
──────────────                   ─────────────────────
                  POST /api/houses
[smart_house]  ────────────────▶ [iot_hub] ◀── browser
               PUT  /keepalive
               PUT  /state
               POST /report_motion
               GET  /state    (when hub asks for it)
               DELETE /api/houses/<id>
```

Every ~1 second each ESP32 sends a keepalive. The hub replies with two flags: `alarm` (buzz now) and `state_update` (pull new state, the dashboard changed something).

If any armed house reports motion, the hub sets the alarm flag on **every** armed house — global alarm.

---

## Pre-camp setup (do this ONCE on a laptop with internet)

You'll end up with a USB stick / shared folder containing everything needed to install offline at camp.

### 1. Get the code on the staging laptop
```bash
git clone <your-repo-url> sigma-camp
cd sigma-camp/claude
```

### 2. Pre-download Flask + flashing tools as wheels

```bash
cd implementation/iot_hub
mkdir wheels
py -3 -m pip download -d wheels -r requirements.txt
py -3 -m pip download -d wheels esptool==4.7.0 mpremote==1.22.0
```

You should now have `~10 .whl` files in `iot_hub/wheels/`. These will be installed offline at camp.

### 3. Download MicroPython firmware for the ESP32

Grab the latest stable build from <https://micropython.org/download/ESP32_GENERIC/> (verify the URL/version — it changes). Save the `.bin` into `smart_house/firmware/`:

```bash
mkdir -p ../smart_house/firmware
# Example URL — replace with the current release before camp:
curl -L -o ../smart_house/firmware/ESP32_GENERIC-v1.23.0.bin \
     https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin
```

### 4. Download Thonny (for ESP32 work)

Grab the standalone installer from <https://thonny.org/> — same Windows installer for every camp laptop. Drop it on the USB stick alongside the code. Thonny includes its own Python so the campers don't need anything else for the ESP32 side.

### 5. Test the offline install on the staging laptop

Verify the wheels work without internet **before** you trust them at camp:

```bash
# In a fresh venv:
py -3 -m venv .venv
source .venv/Scripts/activate     # bash; on cmd use: .venv\Scripts\activate
py -3 -m pip install --no-index --find-links wheels -r requirements.txt
py -3 -m pip install --no-index --find-links wheels esptool mpremote
py -3 app.py
# Open http://localhost:8080/  -> empty dashboard.
```

If the page loads with "Waiting for houses to register…", the offline install works.

### 6. Flash one ESP32 to confirm the firmware

```bash
py -3 -m esptool --port COM5 erase_flash
py -3 -m esptool --port COM5 --baud 460800 write_flash -z 0x1000 \
     ../smart_house/firmware/ESP32_GENERIC-v1.23.0.bin
```

(replace `COM5` with the actual port — `mode` in Device Manager → Ports lists it).

Now copy `implementation/smart_house/secrets_example.py` → `secrets.py`, fill in WiFi + hub URL, then upload the smart_house code to the board:

```bash
cd ../smart_house
py -3 -m mpremote connect COM5 fs cp lcd_api.py :lcd_api.py
py -3 -m mpremote connect COM5 fs cp lcd_i2c.py :lcd_i2c.py
py -3 -m mpremote connect COM5 fs cp config.py :config.py
py -3 -m mpremote connect COM5 fs cp secrets.py :secrets.py
py -3 -m mpremote connect COM5 fs cp hub_client.py :hub_client.py
py -3 -m mpremote connect COM5 fs cp app_sync.py :app_sync.py
py -3 -m mpremote connect COM5 fs cp app_async.py :app_async.py
py -3 -m mpremote connect COM5 fs cp main.py :main.py
py -3 -m mpremote connect COM5 fs mkdir devices
py -3 -m mpremote connect COM5 fs cp devices/. :devices/
```

Reset the ESP32 — the LCD should show "Connecting…" then "Ready". Refresh the dashboard — the new house appears.

(At camp, students will do this through Thonny's GUI instead of `mpremote` — much friendlier. The `mpremote` route above is only for your verification.)

---

## At camp (offline workflow)

### On the counsellor laptop (the hub)

1. Plug into the camp router (or hotspot the laptop and have ESP32s join it).
2. Find the laptop's IP: `ipconfig` (Windows). Note something like `192.168.1.42`.
3. Open the `iot_hub` folder in **PyCharm Community**:
   - File → Open → `claude/implementation/iot_hub`
   - PyCharm will see `requirements.txt` and offer to create a venv. Accept.
   - When it tries to install Flask and fails (no internet), open Settings → Project → Python Interpreter → ⚙️ → "Show all" → "+" → tick **"Use options"** and add `--no-index --find-links C:/path/to/claude/implementation/iot_hub/wheels` → search for `Flask` and install. (Or just open the terminal panel inside PyCharm and run `pip install --no-index --find-links wheels -r requirements.txt`.)
4. Right-click `app.py` → **Run 'app'**. Hub is up at `http://<laptop-ip>:8080`.
5. Allow inbound port 8080 in Windows Firewall when prompted.

### On each ESP32 (one per camper / team)

1. Open **Thonny** (already pre-installed from the USB).
2. **Tools → Options → Interpreter → MicroPython (ESP32)**, pick the COM port. (If the board is fresh, install the firmware: same dialog has "Install or update MicroPython" → pick the `.bin` from the USB.)
3. Copy `secrets_example.py` → `secrets.py` and edit the three lines (WiFi name, password, `HUB_URL = "http://<laptop-ip>:8080"`).
4. In Thonny's file browser, select all the `smart_house/` files (and the `devices/` folder), right-click → **Upload to /**.
5. Hit the ESP32's RESET button. LCD shows "Connecting…" → "Ready 6chars".
6. Refresh the dashboard in the laptop browser. The new house appears.
7. Click **off** under LED in the dashboard → physical LED switches on within 1 second.
8. Wave a hand over the PIR sensor while alarm is armed → buzzer fires on every armed house.

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| LCD shows "WiFi FAILED" | Wrong SSID/password in `secrets.py` | Edit and re-upload |
| Board appears in dashboard but goes "Lost" after a minute | Hub URL wrong, or laptop firewall blocking 8080 | Check `HUB_URL`, allow inbound 8080 |
| Toggle button does nothing | Hub running, but board not polling — check Thonny REPL for HTTP errors | Reset the board |
| `pip install` complains about no internet | Forgot `--no-index --find-links wheels` | Re-run with those flags |

---

## Project layout

```
claude/
├── README.md                       # this file
├── PLAN.md                         # the design plan
├── tutorial/                       # 5-day curriculum + counsellor guide + slides
└── implementation/                 # the running code
    ├── iot_hub/                    # Flask hub (counsellor laptop, opens in PyCharm)
    │   ├── app.py                  # routes
    │   ├── houses.py               # in-memory data layer
    │   ├── constants.py            # magic numbers
    │   ├── requirements.txt        # Flask==3.0.3
    │   ├── templates/index.html
    │   ├── static/dashboard.js
    │   └── static/style.css
    └── smart_house/                # MicroPython firmware (ESP32, uploads via Thonny)
        ├── README.md               # firmware-specific notes
        ├── main.py                 # boot entry; picks sync or async
        ├── config.py               # pins + flags
        ├── secrets_example.py      # template -> copy to secrets.py
        ├── hub_client.py           # the only HTTP code
        ├── app_sync.py             # default: while-True loop
        ├── app_async.py            # advanced: uasyncio version
        ├── lcd_api.py              # vendor LCD driver
        ├── lcd_i2c.py              # vendor LCD driver
        └── devices/
            ├── led.py
            ├── button.py
            ├── motion.py
            ├── fan.py
            ├── buzzer.py
            └── lcd.py
```
