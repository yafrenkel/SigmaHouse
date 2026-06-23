# smart_house — ESP32 firmware

MicroPython firmware for the Keyestudio ESP32 Smart Home kit. Each "house" is one ESP32 board that talks to the iot_hub server over WiFi.

## What's on the board

| Pin | Component | What it does |
|---:|---|---|
| 12 | LED | Light bulb you can switch on/off |
| 26 | Button A | Cycles the LCD menu (LED → FAN → BUZZER) |
| 25 | Button B | Toggles the device shown on the LCD |
| 13 | PIR motion sensor | Reports motion to the hub |
| 18, 19 | Fan (H-bridge) | Two-pin PWM motor |
| 4 | Buzzer | Alarm tone |
| 22 (SCL), 21 (SDA) | I2C bus | LCD1602 display @ address 0x27 |

## Files

| File | What it is |
|---|---|
| `main.py` | Auto-runs on boot. Picks sync or async based on `USE_ASYNC` in config. |
| `config.py` | Pin numbers, hub URL (via `secrets.py`), flags. **Edit this to retune anything.** |
| `secrets_example.py` | Template — copy to `secrets.py` and put your real WiFi creds in. |
| `app_sync.py` | **DEFAULT.** One simple while-True loop. Read this first. |
| `app_async.py` | Advanced version using `uasyncio`. Same behavior, different shape. |
| `hub_client.py` | The only file that talks HTTP to the hub. Used by both apps. |
| `devices/led.py`, `button.py`, `motion.py`, `fan.py`, `buzzer.py`, `lcd.py` | One device per file. |
| `lcd_api.py`, `lcd_i2c.py` | Vendor LCD driver. Don't edit. |

## First-time setup (Thonny)

1. Plug the ESP32 in via USB.
2. Open Thonny. **Tools → Options → Interpreter** → MicroPython (ESP32) → pick the COM port.
3. If the board is blank: **Tools → Options → Interpreter → Install or update MicroPython**, then point at `claude/implementation/smart_house/firmware/ESP32_GENERIC-*.bin` (downloaded once before camp — see `claude/README.md`).
4. Copy `secrets_example.py` to `secrets.py` (Thonny: right-click → Save copy as → "secrets.py" on the board).
5. Edit `secrets.py` with your WiFi name, password, and hub URL (e.g. `http://192.168.1.42:8080`).
6. Upload every file from this folder to the board (Thonny: select files in the local pane → right-click → Upload to /). Make sure `devices/` is uploaded as a folder.
7. Press the ESP32's RESET button. The LCD should show "Connecting..." then "Ready" with the last 6 chars of the board's MAC.

## Switching to the async version

Open `config.py` on the board, change `USE_ASYNC = False` to `USE_ASYNC = True`, save, reset the board. Same behavior — different code shape. Compare the two files side by side to see what `async/await` changes.
