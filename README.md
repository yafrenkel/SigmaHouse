# Sigma Camp IoT — Smart Houses

A summer-camp project for campers with some Python experience. You build a
tiny **smart house** on an ESP32 board and connect it to a **hub** (a small web
server) that shows every house on a live dashboard and can control them.

Two parts:

- **`implementation/iot_hub/`** — a Flask web server + dashboard. Runs on a
  computer (yours at home, or a counsellor's laptop at camp).
- **`implementation/smart_house/`** — MicroPython firmware for the ESP32
  (Keyestudio Smart Home kit). Each board joins WiFi, registers with the hub,
  reports its state, and obeys commands from the dashboard.

They talk over plain HTTP. At camp everything runs on the **local WiFi only** (no
internet needed) — but to set it up **at home you just use your normal WiFi**.

## How they talk to each other

```
ESP32 board                       Your computer
──────────────                   ─────────────────────
                  POST /api/houses
[smart_house]  ────────────────▶ [iot_hub] ◀── browser (dashboard)
               PUT  /keepalive
               PUT  /state
               POST /report_motion
               GET  /state    (when the hub asks for it)
               DELETE /api/houses/<id>
```

Every ~1 second each ESP32 sends a **keepalive**. The hub replies with flags:
`alarm` (buzz now), `state_update` (pull new state — the dashboard changed
something), and `message` (you've got mail — the Day-5 messaging bonus). If any
armed house reports motion, the hub raises the alarm on **every** armed house.

---

## Set it up at home (with internet)

Do this on your own computer to try the whole thing yourself.

**You need:** Python 3.10+ , an ESP32 (Keyestudio Smart Home kit), a USB data
cable, and WiFi. Your computer and the board must be on the **same WiFi**, and it
must be **2.4 GHz** — an ESP32 cannot see 5 GHz networks.

### 1. Get the code

```bash
git clone https://github.com/yafrenkel/SigmaHouse.git
cd SigmaHouse
git checkout 2026
```

### 2. Run the hub (the web server + dashboard)

```bash
cd implementation/iot_hub
python -m venv .venv
# Windows (PowerShell):   .venv\Scripts\Activate.ps1
# Windows (cmd):          .venv\Scripts\activate
# Mac / Linux:            source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:8080/> — you should see **"Waiting for houses to
register…"**. Leave it running.

Now find your computer's address on the WiFi, so the board can reach it:

- **Windows:** `ipconfig` → look for "IPv4 Address" (e.g. `192.168.1.42`)
- **Mac/Linux:** `ipconfig getifaddr en0` or `ip addr`

Your board's hub URL will be `http://<that-ip>:8080` (e.g. `http://192.168.1.42:8080`).
If your firewall asks, **allow** incoming connections on port 8080.

### 3. Set up the ESP32 board (Thonny + MicroPython)

1. Install **Thonny** from <https://thonny.org/> (it includes its own Python — no
   extra setup for the board side).
2. Plug in the board. In Thonny: **Tools → Options → Interpreter →
   MicroPython (ESP32)**, and pick the board's serial port.
   - **Fresh board?** The same dialog has **"Install or update MicroPython"** —
     use it to download and flash the latest `ESP32_GENERIC` firmware.
   - **No port shows up?** You probably need the USB-serial driver for your board:
     **CH340** (`CH341SER`) or **CP210x** — install it, then replug.
3. Make your own secrets file: copy
   `implementation/smart_house/secrets_example.py` to **`secrets.py`** in that
   same folder, and set the three lines to **your** values:
   ```python
   WIFI_SSID = "your WiFi name"
   WIFI_PASS = "your WiFi password"
   HUB_URL   = "http://192.168.1.42:8080"   # your computer's IP from step 2
   ```
   (`secrets.py` is gitignored on purpose — it holds your password, so it never
   gets committed.)
4. In Thonny's **Files** pane, open the `implementation/smart_house/` folder on
   your computer. Select these and right-click → **Upload to /**:
   `main.py`, `config.py`, `secrets.py`, `hub_client.py`, `app_sync.py`,
   `app_async.py`, `lcd_api.py`, `lcd_i2c.py`, and the whole **`devices/`** folder.

### 4. See it work

Press the board's **RESET** button. The LCD shows **"Connecting…"** then
**"Ready"** with an IP. Refresh the dashboard in your browser — **your house
appears!** Click **off** under LED → the real LED turns on within a second. Wave
your hand over the motion sensor while the alarm is armed → the buzzer fires.

### Common problems

| Symptom | Likely cause | Fix |
|---|---|---|
| LCD shows "WiFi FAILED" | Wrong SSID/password, or a **5 GHz** network | Fix `secrets.py`; use a 2.4 GHz WiFi |
| No serial port in Thonny | Missing USB driver, or a charge-only cable | Install CH340/CP210x driver; use a **data** cable |
| House appears then goes **"Lost"** | Wrong `HUB_URL`, or firewall blocking 8080 | Check the IP in `secrets.py`; allow port 8080 |
| Dashboard button does nothing | Board not polling — check the Thonny shell for errors | Reset the board |
| `wlan.scan()` returns `[]` | The network is 5 GHz only | Use a 2.4 GHz network / phone hotspot |

---

## Curriculum & bonus material

- **`tutorial/`** — the 5-day lesson pages (`day1.html` … `day5.html`), plus
  `circuits.html`, `PWM.html`, a glossary, and the buzzer-music bonus
  (`day5_music.html`). Open `tutorial/INDEX.html` to start.
- **`examples/`** — small runnable programs per day, including
  `examples/bonus_music/` (a melody player, 16 tunes, and a multi-board
  "orchestra").

---

## For counsellors: prepare an OFFLINE camp bundle

At camp there is no internet, so pre-download everything **once** on a laptop with
internet, then copy it to a USB stick / shared folder.

### 1. Pre-download Flask as wheels

```bash
cd implementation/iot_hub
mkdir wheels
python -m pip download -d wheels -r requirements.txt
python -m pip download -d wheels esptool==4.7.0 mpremote==1.22.0
```

### 2. Download the ESP32 firmware

Grab the latest stable build from
<https://micropython.org/download/ESP32_GENERIC/> and save the `.bin` into
`implementation/smart_house/firmware/` (create the folder). Verify the version —
it changes.

### 3. Download Thonny

Grab the standalone installer from <https://thonny.org/> and drop it on the USB
stick. Thonny bundles its own Python for the board side.

### 4. Test the offline install before you trust it

```bash
python -m venv .venv
source .venv/Scripts/activate        # bash; on cmd use: .venv\Scripts\activate
python -m pip install --no-index --find-links wheels -r requirements.txt
python app.py                        # open http://localhost:8080/
```

### At camp (offline)

- **Hub laptop:** open `implementation/iot_hub` in **PyCharm Community** (or a
  terminal). Create the venv and install from the local wheels:
  `pip install --no-index --find-links wheels -r requirements.txt`, then run
  `app.py`. Find the laptop IP with `ipconfig` and allow port 8080 in the firewall.
- **Each ESP32:** flash MicroPython from the USB via Thonny's "Install or update
  MicroPython", copy `secrets_example.py` → `secrets.py` with the camp WiFi + the
  laptop's `HUB_URL`, then upload the `smart_house/` files as in the home steps.

> `wheels/`, `firmware/`, `*.bin`, and every `secrets.py` are gitignored — they
> stay on the USB stick, never in the repo.

---

## Project layout

```
SigmaHouse/
├── README.md                       # this file
├── PLAN.md                         # the design plan
├── tutorial/                       # 5-day curriculum, references, bonus pages
│   └── INDEX.html                  # start here
├── examples/                       # per-day runnable programs
│   └── bonus_music/                # melody player + multi-board orchestra
└── implementation/                 # the running code
    ├── iot_hub/                    # Flask hub (runs on a computer)
    │   ├── app.py                  # routes
    │   ├── houses.py               # in-memory data layer
    │   ├── constants.py            # tunable numbers
    │   ├── requirements.txt        # Flask
    │   ├── templates/index.html
    │   └── static/dashboard.js, style.css
    └── smart_house/                # MicroPython firmware (ESP32, upload via Thonny)
        ├── main.py                 # boot entry; picks sync or async
        ├── config.py               # pins + flags
        ├── secrets_example.py      # template -> copy to secrets.py (your WiFi)
        ├── hub_client.py           # the only HTTP code
        ├── app_sync.py             # default: while-True loop
        ├── app_async.py            # advanced: uasyncio version
        ├── lcd_api.py, lcd_i2c.py  # vendor LCD driver
        └── devices/                # led, button, motion, fan, buzzer, lcd
```
