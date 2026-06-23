# Diagrams

Two draw.io diagrams that explain the project visually. Camper-friendly — designed to project on a screen at the start of a session, or print as A4 reference sheets.

| File | What it shows |
|---|---|
| [01_iot_hub.drawio](01_iot_hub.drawio) | The server side: browser, Flask routes, HOUSES dict, watchdog, multiple ESP32 boards |
| [02_smart_house.drawio](02_smart_house.drawio) | The board side: physical peripherals with GPIO pins, software stack inside the ESP32, IRQ rule |
| [03_http_and_server.drawio](03_http_and_server.drawio) | The concept: anatomy of an HTTP request/response, status codes, and the server's listen→match→run→respond loop |

## How to open / edit

### Option A — diagrams.net in browser (no install)
1. Go to <https://app.diagrams.net/>.
2. **Open Existing Diagram → Device** → pick the `.drawio` file.
3. Edit, then **File → Save** or **File → Export as → PNG / PDF**.

### Option B — draw.io desktop app
1. Download once (online): <https://github.com/jgraph/drawio-desktop/releases>. Drop the installer on the USB.
2. Open → File → pick the file.

### Option C — VS Code extension
Install the **Draw.io Integration** extension; `.drawio` files render natively. Probably the smoothest if students already use VS Code.

## Suggested camp use

- **Day 1, very first thing** — project `03_http_and_server.drawio`. Explain the request/response idea and "a server is a loop" BEFORE any code. This is the mental model everything else hangs on.
- **Day 1 morning** — switch to `01_iot_hub.drawio` while explaining what they'll build. Highlight the HOUSES dict and the route list. (It reuses the same colors as diagram 03, so the request/response arrows feel familiar.)
- **Day 2 morning** — switch to `02_smart_house.drawio`. Walk them around the perimeter (hardware) then dive into the software stack.
- **Days 3-4** — leave the matching diagram visible while they code. Students who get lost can look up at the picture instead of asking.
- **Day 5** — both diagrams up; ask the room "where in this picture does your final-project feature live?"

## Exporting to PNG/PDF for printing or slides

In any of the three options above:
- **File → Export as → PNG** for slides (use 2x scale for crispness).
- **File → Export as → PDF** for printing as A4 reference sheets.

Recommended: export both diagrams as PDF, drop them into `tutorial/slides/` so the printable versions live next to the slide decks.

## Customising

Free game. Common tweaks:
- **Replace the laptop's IP** in `01_iot_hub.drawio` with your camp's real IP.
- **Add your camp's logo** as a background image (Edit → Background → Image).
- **Re-arrange for projector aspect ratio** — diagrams are designed for 4:3; for 16:9 widen the page and stretch boxes.
- **Add an "extras" diagram** if you want a third (e.g. show how the watchdog state machine works, or how the alarm propagation walks the dict).

If you tweak heavily and want it back to the original, the files are git-controlled — `git checkout` brings them back.
