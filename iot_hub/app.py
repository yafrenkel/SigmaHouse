"""Main Flask app."""
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from connexion import App

from flask import render_template

from houses import HOUSES

app = App(__name__, specification_dir="./")
app.add_api("openapi.yaml")


def watchdog():
    """De-activate houses based on last keep-alive timestamp."""
    for unique_id in HOUSES:
        try:
            last_seen_time = datetime.strptime(
                HOUSES[unique_id]["timestamp_keepalive"], "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            last_seen_time = datetime.now()

        last_seen_duration_seconds = (datetime.now() - last_seen_time).total_seconds()

        if (
            HOUSES[unique_id]["status"] != "Deleted"
            and HOUSES[unique_id]["status"] != "Lost"
            and last_seen_duration_seconds > 60
        ):
            HOUSES[unique_id].update(
                {
                    "status": "Lost",
                    "state": {
                        "alarm": {
                            "triggered": False,
                            "armed": False,
                            "mode": 0,
                            "armed_timestamp": 0,
                            "triggered_timestamp": 0,
                            "disarmed_timestamp": 0,
                        },
                        "buzzer": {
                            "active": False,
                            "timestamp": 0,
                        },
                        "fan": {
                            "active": False,
                            "clockwise": True,
                            "timestamp": 0,
                        },
                        "led": {
                            "active": False,
                            "timestamp": 0,
                        },
                        "motion": {
                            "motion_detected": False,
                            "triggered_timestamp": 0,
                            "released_timestamp": 0,
                        },
                    },
                }
            )


@app.route("/")
def hello_world():
    """Serve test page."""
    return render_template("hello_world.html")


@app.route("/ui")
def ui_index():
    """Serve dashboard page."""
    return render_template("ui_index.html", houses=HOUSES)


@app.route("/static/list_houses")
def list_houses():
    """Show list of houses."""
    return render_template("list_houses.html", houses=HOUSES)


if __name__ == "__main__":
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=watchdog, trigger="interval", seconds=20)
    scheduler.start()

    app.run(
        host="0.0.0.0", port=8080, debug=True, use_reloader=False  # noqa: S201, S104
    )

    scheduler.shutdown()
