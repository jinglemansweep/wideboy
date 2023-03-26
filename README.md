# WideBoy

![WideBoy: Ultra Wide Display System](./docs/images/logo-header.png)

## Media

![Wideangle Photo of WideBoy Display](./docs/images/photo-wide-01.png)

## Features

- :alarm_clock: Clock (NTP managed)
- :calendar: Basic calendar (reminders coming soon)
- :sunny: Weather summary and next hour forecast
- :camera: Background image slideshow (great with [ArtyFarty](https://github.com/jinglemansweep/artyfarty) AI art generator)
- :incoming_envelope: Announcements and notifications via [MQTT](https://en.wikipedia.org/wiki/MQTT)
- :satellite: Remote control via MQTT and [Home Assistant](https://www.home-assistant.io/)
- :strawberry: Optimised for [DietPi](https://dietpi.com/) running on a Raspberry Pi 4

## Installation

Fetch dependencies submodules:

    git submodule update --init --recursive

Build `rpi-rgb-led-matrix` Python bindings:

    cd lib/rpi-rgb-led-matrix
    make build-python

## Development

Create a Python 3.x virtual environment, and install project dependencies:

    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip poetry
    poetry install

## Running

To run the project:

    . venv/bin/activate
    python3 -m wideboy
