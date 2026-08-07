"""hello_iot.py -- a teaching bridge between hello.py and app.py.

This is ONE file on purpose. The real hub (app.py) splits its work across
app.py + houses.py + constants.py + templates/. That split is great for a
real project but it means you have to jump between four files to follow a
single request. Here, everything lives in one place so you can read it top
to bottom.

Every idea below shows up again in app.py, using the same words (house,
unique_id, keepalive, state, led/fan/buzzer). Once this file makes sense,
open app.py -- you'll recognise the routes instead of meeting them cold.

New things compared to hello.py:
  1. a path parameter in the URL          ->  /api/houses/<uid>
  2. a POST route that reads a JSON body   ->  register a house
  3. state we keep and change over time    ->  the HOUSES dict

Run it:
    python hello_iot.py
Then open:
    http://localhost:8081/

(Port 8081 so it won't collide with app.py on 8080 -- you can run both.)

Try the API from a terminal (curl comes with Windows 10+):
    curl http://localhost:8081/api/houses
    curl -X POST http://localhost:8081/api/houses -H "Content-Type: application/json" -d "{\"unique_id\": \"camp01\"}"
    curl http://localhost:8081/api/houses/camp01
    curl -X POST http://localhost:8081/api/houses/camp01/toggle/led

Or try it from the BROWSER. Open http://localhost:8081/, press F12 for the
developer tools, click "Console", and paste one of these. fetch() is how a web
page talks to a server -- app.py's dashboard uses the very same call.

    // GET the list of houses
    fetch("/api/houses").then(r => r.json()).then(console.log)

    // POST a new house (JSON body -- note method, headers, and body)
    fetch("/api/houses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ unique_id: "camp01" }),
    }).then(r => r.json()).then(console.log)

    // POST to flip its LED (no body needed -- the URL says it all)
    fetch("/api/houses/camp01/toggle/led", { method: "POST" })
      .then(r => r.json()).then(console.log)

After the toggle, refresh the page and watch the LED column change.
(These use short paths like "/api/houses" because you're already ON the page
at localhost:8081 -- the browser fills in the rest.)
"""

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)


# ---------- our "database" ----------
# In hello.py this was a list called `clients`. Here it's a dict keyed by the
# house's unique_id, exactly like HOUSES in houses.py -- just kept right here
# instead of in another file. It empties every time you restart the server.
HOUSES = {}

# The three gadgets a house can switch on and off. Same list as app.py's
# VALID_DEVICES (which lives in constants.py over there).
VALID_DEVICES = ("led", "fan", "buzzer")


def new_house(unique_id, ip_address):
    """Build a fresh house record. Compare with houses.register() in app.py."""
    return {
        "unique_id": unique_id,
        "ip_address": ip_address,
        "state": {
            "led": {"active": False},
            "fan": {"active": False},
            "buzzer": {"active": False},
        },
    }


# ---------- the dashboard page ----------
# Like hello.py, we keep the HTML right here with render_template_string.
# (app.py graduates to a real templates/index.html file -- same idea, own file.)
@app.route("/")
def index():
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>hello_iot dashboard</title>
            <style>
              body  { font-family: Arial, sans-serif; margin: 20px; }
              table { border-collapse: collapse; }
              th, td { padding: 8px 12px; border: 1px solid #ccc; }
              .on  { color: green; font-weight: bold; }
              .off { color: #999; }
            </style>
          </head>
          <body>
            <h1>Registered Houses</h1>
            {% if houses %}
            <table>
              <tr><th>Unique ID</th><th>IP</th><th>LED</th><th>Fan</th><th>Buzzer</th></tr>
              {% for h in houses %}
              <tr>
                <td>{{ h.unique_id }}</td>
                <td>{{ h.ip_address }}</td>
                {% for d in ['led', 'fan', 'buzzer'] %}
                  {% if h.state[d].active %}
                    <td class="on">ON</td>
                  {% else %}
                    <td class="off">off</td>
                  {% endif %}
                {% endfor %}
              </tr>
              {% endfor %}
            </table>
            {% else %}
            <p>No houses yet. Register one with the API (see the curl commands
               at the top of hello_iot.py).</p>
            {% endif %}
          </body>
        </html>
        """,
        houses=list(HOUSES.values()),
    )


# ---------- the API ----------

# GET: list every house. Nothing new yet -- this is hello.py's /smart idea,
# just returning the whole collection.
@app.route("/api/houses", methods=["GET"])
def list_houses():
    return jsonify(list(HOUSES.values()))


# POST: register a house. NEW: this reads a JSON body instead of ?query=args.
# The camper sends {"unique_id": "camp01"} and we store a record for it.
@app.route("/api/houses", methods=["POST"])
def register_house():
    body = request.get_json(silent=True) or {}
    unique_id = body.get("unique_id")
    if not unique_id:
        return jsonify({"error": "unique_id required"}), 400
    HOUSES[unique_id] = new_house(unique_id, request.remote_addr)
    return jsonify({"ok": True, "unique_id": unique_id}), 201


# GET one house. NEW: <uid> is a PATH parameter -- whatever you put in the URL
# arrives as the `uid` argument. Compare app.py's /api/houses/<uid>/state.
@app.route("/api/houses/<uid>", methods=["GET"])
def get_house(uid):
    house = HOUSES.get(uid)
    if house is None:
        return jsonify({"error": "unknown house"}), 404
    return jsonify(house)


# POST: flip a gadget on or off. Two path params this time: which house, and
# which device. This is a shrunk-down houses.toggle_device().
@app.route("/api/houses/<uid>/toggle/<device>", methods=["POST"])
def toggle(uid, device):
    if device not in VALID_DEVICES:
        return jsonify({"error": f"device must be one of {VALID_DEVICES}"}), 400
    house = HOUSES.get(uid)
    if house is None:
        return jsonify({"error": "unknown house"}), 404
    current = house["state"][device]["active"]
    house["state"][device]["active"] = not current
    return jsonify({"ok": True, device: not current})


# ---------------------------------------------------------------------------
# ADD YOUR OWN ROUTE BELOW
# ---------------------------------------------------------------------------
# Copy this template and make it yours. Ideas to try:
#   * /api/houses/<uid>/rename  -- read a new name from the JSON body
#   * /api/houses/<uid>         with methods=["DELETE"] to remove a house
#   * /api/count                -- return how many houses are registered
#
# @app.route("/api/houses/<uid>/hello", methods=["GET"])
# def say_hello(uid):
#     house = HOUSES.get(uid)              # 1. look the house up
#     if house is None:                    # 2. always handle "not found"
#         return jsonify({"error": "unknown house"}), 404
#     return jsonify({"message": f"Hello, house {uid}!"})   # 3. return JSON
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # debug=True auto-reloads on save and shows errors in the browser.
    app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=False)
