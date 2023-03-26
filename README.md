# WideBoy: Ultra Wide Display System

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
- :white_square_button: QR code display for easy linking from mobile devices
- :strawberry: Optimised for [DietPi](https://dietpi.com/) running on a Raspberry Pi 4

## Components

### Hardware

- :strawberry: Raspberry Pi 4 (2GB RAM or higher) (see [RPi Locator](https://rpilocator.com/) for availablity)
- :tophat: Active HUB75 Raspberry Pi Hat (e.g. [Electrodragon RGB Matrix Panel Driver Board](https://www.electrodragon.com/product/rgb-matrix-panel-drive-board-raspberry-pi/))
- :black_medium_square: 12 x 64x64 or 6 x 128x64 HUB75e LED matrix panels (e.g. [P2 P2.5 Indoor SMD2121 Full Color LED Display Module 1/32 Scan 320x160mm](https://www.aliexpress.com/item/32845686589.html))
- :zap: 5v power supply with support for 24A+ (e.g. [5v 40A Power Supply](https://www.amazon.co.uk/inShareplus-Universal-Regulated-Switching-Transformer/dp/B08QRCSTG4))

### Software

- :black_medium_square: [RPi RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library to drive HUB75 LED panels with a Raspberry Pi
- :video_game: [PyGame](https://www.pygame.org/) Python based 2D graphics and gaming engine
- :electric_plug: Custom adaptor to reshape and convert PyGame RGB surface to LED matrix compatible pixel array (see [./wideboy/utils/display.py](./wideboy/utils/display.py))
- :strawberry: [DietPi](https://dietpi.com/), a minimal lightweight Linux distribution designed for Raspberry Pi devices
- :snake: Python 3.x, [Paho MQTT Client](https://pypi.org/project/paho-mqtt/), [HomeAssistantAPI](https://github.com/GrandMoff100/HomeAssistantAPI)

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
