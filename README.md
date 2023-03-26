# WideBoy: Ultra Wide Display System

![WideBoy: Ultra Wide Display System](./docs/images/logo-header.png)

Wideboy is an experimental project that provides an ultra wide video wall display, serving dashboards, art/image slideshows and notification alerts. It is developed using Python and PyGame, providing smooth and fast animations, and is designed to run on Raspberry Pi single board computers for both energy-efficient and cost-effective operation.

This project is perfect for delivering dynamic visual content that can entertain and keep your home or office informed, whether you want to convey important information, display beautiful visuals, or create an immersive experience.

## Photos & Screenshots

Main installation on living room shelf, accompanied by [WLED](https://kno.wled.ge/) controlled NeoPixel lighting strips:

![Wideangle Photo of WideBoy Display](./docs/images/photo-wide-01.png)

Idle background slideshow and clock displaying AI generated tiled chocolate bar imagery:

![Background Slideshow: Chocolate](./docs/images/screenshot-background-chocolate.jpg)

Another AI generated background slideshow example:

![Background Slideshow: Alan Sugar](./docs/images/screenshot-background-alan-sugar.jpg)

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

- :strawberry: Raspberry Pi 4 (2GB RAM or higher) (see [RPi Locator](https://rpilocator.com/) for availability)
- :tophat: Active HUB75 Raspberry Pi Hat (e.g. [Electrodragon RGB Matrix Panel Driver Board](https://www.electrodragon.com/product/rgb-matrix-panel-drive-board-raspberry-pi/))
- :black_medium_square: 12 x 64x64 or 6 x 128x64 HUB75e LED matrix panels (e.g. [P2 P2.5 Indoor SMD2121 Full Color LED Display Module 1/32 Scan 320x160mm](https://www.aliexpress.com/item/32845686589.html))
- :zap: 5v power supply with support for 24A+ (e.g. [5v 40A Power Supply](https://www.amazon.co.uk/inShareplus-Universal-Regulated-Switching-Transformer/dp/B08QRCSTG4))

### Software

- :black_medium_square: [RPi RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library to drive HUB75 LED panels with a Raspberry Pi
- :video_game: [PyGame](https://www.pygame.org/) Python based 2D graphics and gaming engine
- :electric_plug: Custom adaptor to reshape and convert PyGame RGB surface to LED matrix compatible pixel array (see [./wideboy/utils/display.py](./wideboy/utils/display.py))
- :penguin: [DietPi](https://dietpi.com/), a minimal lightweight Linux distribution designed for Raspberry Pi devices
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

## Technical Details

### Surface Reshaping

The actual PyGame "Game Surface" is comprised of 12 LED panels (64px x 64px each) in a 12 x 1 layout, with a total resolution of 768 pixels wide by 64 pixels high. To achieve reasonable frame rates, it is neccesary to drive the panels in three parallel chains. Each of the three chains consists of 4 panels each (256px x 64px).

However, the RGB Matrix library expects to render each chain on a different row (e.g. 4 panels wide by 3 panels high). In order to workaround this, it is necessary to reshape the game surface on every frame before sending the pixel array to the LED panels. This is performed by converting the PyGame game surface into a Numpy nparray, and then transposing slices of the 2D pixel array into the required layout. The following diagram helps explain the process:

![Diagram showing remapping of PyGame game surface into required 2D pixel array](./docs/images/technical-surface-reshape.png)
