# Smart House

[![Python 3.7+](https://img.shields.io/badge/Python-3.8+-blue.svg)][PythonRef] [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)][BlackRef] [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)][MITRef]

This repo contains code to demonstrate IoT and Smart House concepts with [Keyestudio KS5009 Smart Home Model Kit][Keyestudio_KS5009]. It also contains project configs for linting with `Flake8` and formatting with `Black` tool.

[PythonRef]: https://docs.python.org/3.8/
[BlackRef]: https://github.com/ambv/black
[MITRef]: https://opensource.org/licenses/MIT
[Keyestudio_KS5009]: https://wiki.keyestudio.com/KS5009_Keyestudio_Smart_Home

## Required packages

* Connexion 2.14
* Flask 2.2
* Flask-APScheduler 1.12

## Folder `examples`

Contains stand-alone modules to test or demonstrate different aspects of the main Smart House App.

* [day1/wifi_register.py](examples/day1/wifi_register.py) - Graceful WIFI connection with test HTTP POST to the IoT Hub
* [day1/wifi.py](examples/day1/wifi.py) - Graceful WIFI connection
* [day2/button_led1.py](examples/day2/button_led1.py) - Single button press detection and LED toggle
* [day2/button_led2.py](examples/day2/button_led2.py) - Setting LED based on single button state
* [day2/button_led3.py](examples/day2/button_led3.py) -
* [day2/button_led4.py](examples/day2/button_led4.py) -
* [day2/button_led5.py](examples/day2/button_led5.py) -
* [day2/button1.py](examples/day2/button1.py) -
* [day2/button2.py](examples/day2/button2.py) -
* [day2/button3.py](examples/day2/button3.py) -
* [day2/button4.py](examples/day2/button4.py) -
* [day2/button5.py](examples/day2/button5.py) -
* [day2/button6.py](examples/day2/button6.py) -
* [day2/led1.py](examples/day2/led1.py) -
* [day2/led2.py](examples/day2/led2.py) -
* [day2/led3.py](examples/day2/led3.py) -
* [day2/uptime.py](examples/day2/uptime.py) -
* [day3/buzzer1.py](examples/day3/buzzer1.py) - Play hardcoded melody with buzzer
* [day3/buzzer2.py](examples/day3/buzzer2.py) - Play parametrized melody with buzzer
* [day3/buzzer3.py](examples/day3/buzzer3.py) - Play parametrized melody with buzzer using hardware timer
* [day3/buzzer4.py](examples/day3/buzzer4.py) - Buzzer class playing parametrized melody using hardware timer

## Folder `iot_hub`

Contains Flask-based implementation of IoT Hub API (published at `/smarthouse/v1`) and UI (published at `/ui`) server to communicate with all registered Smart House App clients (house models) and manage them remotely.

Implements the following:

* [X] IoT Hub API based on OpenAPI specification from [openapi.yaml](iot_hub/openapi.yaml)
* [X] Tracking of client status as `Registered`, `Active` or `Deleted`
* [X] Watchdog marking clients as `Lost` if no keepalive message received for more than 20 seconds
* [X] Dashboard using JavaScript Fetch API to show houses with dynamic status, timestamps and state
* [X] Edit state of actuators like LED or Fan with dashboard
* [ ] Group alarm functionality triggering alarm on all registered and armed houses based on alarm state of one of them

## Folder `smart_house`

Contains Smart House App providing functionality to support interactions with the Smart House model as well as with the `iot_hub` server to manage all Smart House models registered with the IoT Hub within the same network.

Implements the following:

* [X] Centralized config with sensitive parameters
* [X] Class to manage the app itself
  * [X] Async event-driven processing of user and sensor inputs
* [X] Class to manage WIFI connection
  * [X] Check if configured SSID is on the air
  * [X] Graceful connect with connection timeout
  * [X] Graceful disconnect if app encounters exceptions
* [X] Base class for abstract device with state
* [X] Class to manage simple LED
* [X] Class to process input from buttons with interrupts
* [X] Class to manage fan
* [X] Class to manage PIR sensor
* [X] Class to manage LCD display
* [X] Class to manage single-level text menu for UI (LCD + buttons)
* [X] Class to manage buzzer
* [X] Class to manage alarm system (PIR + buzzer)
* [X] App method to register Smart House with the IoT Hub
* [X] App method to send keep-alive messages from Smart House to the IoT Hub
* [X] App method to delete Smart House from the IoT Hub
* [X] App method to update the IoT Hub with state from Smart House sensors
* [X] App method to update the Smart House with state from the IoT Hub

To run, upload content to ESP32 and make sure `secrets-example.py` is renamed `secrets-example.py` and has correct SSID and password to establish WIFI connection.

## Notes

To emulate connectivity issues between Smart House App client and the IoT Hub server use firewall to block network communication.

Following CLI commands could be used on `Ubuntu`.

* To enable `ufw` and allow communication:

  ```sh
  sudo ufw enable
  sudo ufw allow from CLIENT_IP to SERVER_IP port 8080
  sudo ufw status
  ```

* To block communication with TCP RST so the client gets immediate response

  ```sh
  sudo ufw reject from CLIENT_IP to SERVER_IP port 8080
  sudo ufw status
  ```

* To disable `ufw`

  ```sh
  sudo ufw disable
  ```
