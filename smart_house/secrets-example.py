# -*- coding: utf-8 -*-
"""Contains passwords, auth tokens and other sensitive settings.

NOTE: this file **must be excluded** from git commits or sharing
"""

secret_config = {
    "wifi_ssid": "SmartHome_IoT_Net",
    "wifi_pass": "SecretSquirrelSavesTheDay",
    "api_endpoint": "http://192.168.15.42/smarthouse/v1",
    "update_interval_ms": 1000,
}
