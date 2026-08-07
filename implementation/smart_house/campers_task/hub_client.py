"""HTTP client for talking to the IoT hub.

Both app_sync and app_async use this -- it's the only file that knows
about urequests. Every method:
  - returns a dict on success, or None on failure
  - prints the error so you can see it on the REPL
  - ALWAYS closes the response (urequests leaks sockets otherwise)
"""

import urequests


class HubClient:
    def __init__(self, hub_url, unique_id):
        self.hub_url = hub_url.rstrip("/")
        self.unique_id = unique_id

    # ---------- internal helpers ----------

    def _url(self, path):
        return self.hub_url + path

    def _request(self, method, path, body=None):
        url = self._url(path)
        try:
            if body is None:
                resp = urequests.request(method, url)
            else:
                resp = urequests.request(
                    method, url, json=body,
                    headers={"Content-Type": "application/json"},
                )
        except Exception as e:
            print("HTTP error:", method, url, e)
            return None
        try:
            if resp.status_code >= 400:
                print("HTTP", resp.status_code, method, url)
                return None
            try:
                return resp.json()
            except Exception:
                return {}
        finally:
            resp.close()

    # ---------- public API ----------

    def register(self, ip):
        return self._request(
            "POST", "/api/houses",
            {"unique_id": self.unique_id, "ip_address": ip},
        )

    def keepalive(self, ip):
        """Returns {'alarm': bool, 'state_update': bool} or None."""
        return self._request(
            "PUT", "/api/houses/" + self.unique_id + "/keepalive",
            {"ip_address": ip},
        )

    def get_state(self):
        return self._request("GET", "/api/houses/" + self.unique_id + "/state")

    def push_state(self, state):
        return self._request(
            "PUT", "/api/houses/" + self.unique_id + "/state",
            {"state": state},
        )

    def report_motion(self):
        return self._request(
            "POST", "/api/houses/" + self.unique_id + "/report_motion",
        )

    # ---------- messages (Day 5) ----------

    def send_message(self, to_uid, text):
        """Leave a short message in ANOTHER house's mailbox (to_uid).

        The 'from' is our own unique_id, so the other house knows who wrote.
        """
        return self._request(
            "POST", "/api/houses/" + to_uid + "/messages",
            {"from": self.unique_id, "text": text},
        )

    def get_messages(self):
        """Read (and empty) OUR mailbox. Returns {'messages': [ {from, text, time}, ... ]}."""
        return self._request(
            "GET", "/api/houses/" + self.unique_id + "/messages",
        )

    def get_houses(self):
        """The whole roster -- a LIST of house dicts. Handy for choosing a
        recipient or broadcasting to everyone."""
        return self._request("GET", "/api/houses")

    def deregister(self):
        return self._request("DELETE", "/api/houses/" + self.unique_id)
