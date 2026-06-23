"""IoT hub web server.

Run with:  python app.py
Then open: http://localhost:8080/

Endpoints:
  GET    /                                       -> dashboard HTML
  GET    /api/houses                             -> list every house
  POST   /api/houses                             -> register a house
  PUT    /api/houses/<uid>/keepalive             -> heartbeat
  GET    /api/houses/<uid>/state                 -> what should the house do
  PUT    /api/houses/<uid>/state                 -> what the house is doing
  POST   /api/houses/<uid>/toggle/<device>       -> dashboard toggle
  POST   /api/houses/<uid>/arm                   -> dashboard arm/disarm
  POST   /api/houses/<uid>/report_motion         -> device reports motion
  DELETE /api/houses/<uid>                       -> unregister a house
"""

import threading

from flask import Flask, jsonify, render_template, request

import houses
from constants import VALID_DEVICES, WATCHDOG_INTERVAL_S

app = Flask(__name__)


# ---------- pages ----------

@app.route("/")
def index():
    return render_template("index.html")


# ---------- house collection ----------

@app.route("/api/houses", methods=["GET"])
def list_houses():
    return jsonify(houses.list_all())


@app.route("/api/houses", methods=["POST"])
def register_house():
    body = request.get_json(silent=True) or {}
    unique_id = body.get("unique_id")
    ip = body.get("ip_address", request.remote_addr)
    if not unique_id:
        return jsonify({"error": "unique_id required"}), 400
    houses.register(unique_id, ip)
    return jsonify({"ok": True, "unique_id": unique_id}), 201


# ---------- per-house ----------

@app.route("/api/houses/<uid>/keepalive", methods=["PUT"])
def keepalive(uid):
    body = request.get_json(silent=True) or {}
    ip = body.get("ip_address", request.remote_addr)
    result = houses.keepalive(uid, ip)
    if result is None:
        return jsonify({"error": "unknown house"}), 404
    return jsonify(result)


@app.route("/api/houses/<uid>/state", methods=["GET"])
def get_state(uid):
    state = houses.get_state(uid)
    if state is None:
        return jsonify({"error": "unknown house"}), 404
    return jsonify(state)


@app.route("/api/houses/<uid>/state", methods=["PUT"])
def set_state(uid):
    body = request.get_json(silent=True) or {}
    state = body.get("state")
    if not isinstance(state, dict):
        return jsonify({"error": "state object required"}), 400
    if not houses.set_state(uid, state):
        return jsonify({"error": "unknown house"}), 404
    return jsonify({"ok": True})


@app.route("/api/houses/<uid>/toggle/<device>", methods=["POST"])
def toggle(uid, device):
    if device not in VALID_DEVICES:
        return jsonify({"error": f"device must be one of {VALID_DEVICES}"}), 400
    if not houses.toggle_device(uid, device):
        return jsonify({"error": "unknown house"}), 404
    return jsonify({"ok": True})


@app.route("/api/houses/<uid>/arm", methods=["POST"])
def arm(uid):
    body = request.get_json(silent=True) or {}
    armed = bool(body.get("armed", False))
    if not houses.arm_alarm(uid, armed):
        return jsonify({"error": "unknown house"}), 404
    return jsonify({"ok": True, "armed": armed})


@app.route("/api/houses/<uid>/report_motion", methods=["POST"])
def report_motion(uid):
    if not houses.report_motion(uid):
        return jsonify({"error": "unknown house"}), 404
    return jsonify({"ok": True})


@app.route("/api/houses/<uid>", methods=["DELETE"])
def delete_house(uid):
    if not houses.delete(uid):
        return jsonify({"error": "unknown house"}), 404
    return jsonify({"ok": True})


# ---------- watchdog ----------

def _watchdog_tick():
    """Mark stale houses as Lost, then schedule the next tick."""
    houses.mark_lost_if_stale()
    timer = threading.Timer(WATCHDOG_INTERVAL_S, _watchdog_tick)
    timer.daemon = True
    timer.start()


if __name__ == "__main__":
    _watchdog_tick()
    # host=0.0.0.0 -> reachable from ESP32 on the local network.
    # Port 8080 chosen because port 80 needs admin on Windows.
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
