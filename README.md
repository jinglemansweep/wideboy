# WideBoy

[![docker](https://github.com/jinglemansweep/wideboy/actions/workflows/docker.yml/badge.svg)](https://github.com/jinglemansweep/wideboy/actions/workflows/docker.yml)
[![mypy](https://github.com/jinglemansweep/wideboy/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/wideboy/actions/workflows/mypy.yml) [![flake8](https://github.com/jinglemansweep/wideboy/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/wideboy/actions/workflows/flake8.yml) [![black](https://github.com/jinglemansweep/wideboy/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/wideboy/actions/workflows/black.yml) [![codeql](https://github.com/jinglemansweep/wideboy/actions/workflows/codeql.yml/badge.svg)](https://github.com/jinglemansweep/wideboy/actions/workflows/codeql.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<img src="./docs/images/logo-new.png" width="50%" height="50%" alt="WideBoy Logo">

WideBoy was designed to act as a unique home dashboard. It is a custom PyGame application designed to be displayed on HUB75 LED matrix panels, powered by a modern Raspberry Pi.

It displays basic information such as the current date and time, weather information and calendar events. An image carousel sprite is also included to showcase artwork or other images.

WideBoy has extensive [Home Assistant](https://www.home-assistant.io/) support in that it is fully remotely controllable via the [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) integration. Also, a comprehensive animated dynamic Entity grid sprite is provided, where each tile can be configured with it's own style, icon and visibility rules.

![Wideangle Photo of WideBoy Display](./docs/images/photo-wide-01.png)

## Features

- :alarm_clock: Customisable dedicated clock widget
- :calendar: Basic calendar with events and reminders
- :sunny: Weather summary and next hour forecast
- :camera: Background image slideshow (great with [ArtyFarty](https://github.com/jinglemansweep/artyfarty) AI art generator)
- :house: Animated dynamic Home Assistant entity grid
- :incoming_envelope: Announcements and notifications via [MQTT](https://en.wikipedia.org/wiki/MQTT)
- :satellite: Remote control via MQTT and [Home Assistant](https://www.home-assistant.io/)
- :white_square_button: QR code display for easy linking from mobile devices
- :whale: Offical Docker image and example [Compose](./docker-compose.yml) configuration
- :strawberry: Optimised for [DietPi](https://dietpi.com/) running on a Raspberry Pi 4

## Screenshots

Default scene showing background artwork carousel sprite as well as dynamic Home Assistant entity tile grid sprite:

![Default Scene](./docs/images/screenshot-scene-default.png)

Default scene showing real-time incoming MQTT notification message:

![Incoming Notification](./docs/images/screenshot-sprite-notification.png)

Animated starfield scene:

![Animated Starfied](./docs/images/screenshot-scene-starfield.png)

Credits and debugging scene:

![Animated Starfield](./docs/images/screenshot-scene-credits.png)

Home Assistant MQTT Device:

<a href="./docs/images/screenshot-hass-device.png">
  <img src="./docs/images/screenshot-hass-device.png" width="50%" height="50%" alt="Home Assistant Device">
</a>

Home Assistant Entity Tile Grid:

![Home Assistant Entity Tile Grid](./docs/images/screenshot-sprite-tile-grid.png)

## Usage

### MQTT

By default, WideBoy subscribes and publishes to topics starting with `wideboy/<device-id>`. The device ID is automatically generated from the devices MAC address but can be overridden (see [`settings.toml`](./settings.toml)).

If configured to use the same MQTT broker as Home Assistant, WideBoy will automatically advertise and configure itself using Home Assistant's MQTT Discovery mechanism.

Manual MQTT control is also possible, see below for example topic and message formats:

#### Power

    # Turn on
    mosquitto_pub -t "wideboy/example/master/set" -m '{"state": "ON"}'

    # Turn off
    mosquitto_pub -t "wideboy/example/master/set" -m '{"state": "OFF"}'

    # Set display brightness to 50% (100% = 255)
    mosquitto_pub -t "wideboy/example/master/set" -m '{"state": "ON", "brightness": 128}'

#### Scene Control

    # Advance to next scene
    mosquitto_pub -t "wideboy/example/scene_next/set" -m '{"state": "PRESS"}'

    # Switch to 'default' scene
    mosquitto_pub -t "wideboy/example/scene_select/set" -m "default"

    # Switch to 'starfield' scene
    mosquitto_pub -t "wideboy/example/scene_select/set" -m "starfield"

    # Trigger custom scene actions
    mosquitto_pub -t "wideboy/example/action_a/set" -m '{"state": "PRESS"}'
    mosquitto_pub -t "wideboy/example/action_b/set" -m '{"state": "PRESS"}'

#### Notifications / Alerts

    # Display 'Hello World' notification on display
    mosquitto_pub -t "wideboy/example/message/set" -m "Hello World"

#### Debugging

    # Save screenshot (to 'images/screenshots' directory)
    mosquitto_pub -t "wideboy/example/screenshot/set" -m '{"state": "PRESS"}'

#### Sensors

    # Current FPS
    mosquitto_sub -t "wideboy/example/fps/state"

### Entity Tile Grid

The provided Tile Grid sprite relies on Home Assistant's [MQTT Statestream](https://www.home-assistant.io/integrations/mqtt_statestream/) integration which publishes specific entity state changes over MQTT. Each grid tile subscribes to specific entity states and will redraw on change.

Enabling the Statestream integration requires manual changes to Home Assistant's YAML configuration files.

If you have a large number of entities, it is advisable to only publish changes for entities you want to display in the tile grid to avoid overloading the MQTT service. Entities can be whitelisted or blacklisted using the `include` and `exclude` directives.

The following snippet should be added to `configuration.yaml` or equivalent:

    mqtt_statestream:
      base_topic: homeassistant/statestream
      publish_attributes: true
      publish_timestamps: false
      include:
        entity_globs:
          - sensor.speedtest_download_average
          ...

The `statestream_topic_prefix` option in the `homeassistant` section of `settings.toml` will need updating to match the `base_topic` specified above.

Each Entity tile must be created as a Python class which can then be added to Column groups and finally rendered as a full grid. See [`wideboy/scenes/default/tiles.py`](./wideboy/scenes/default/tiles.py) for some examples.

## Components

### Hardware

- :strawberry: Raspberry Pi 4 (2GB RAM or higher) (see [RPi Locator](https://rpilocator.com/) for availability)
- :tophat: Active HUB75 Raspberry Pi Hat (e.g. [Electrodragon RGB Matrix Panel Driver Board](https://www.electrodragon.com/product/rgb-matrix-panel-drive-board-raspberry-pi/))
- :black_medium_square: 12 x 64x64 or 6 x 128x64 HUB75e LED matrix panels (e.g. [P2 P2.5 Indoor SMD2121 Full Color LED Display Module 1/32 Scan 320x160mm](https://www.aliexpress.com/item/32845686589.html))
- :zap: 5v power supply with support for 24A+ (e.g. [5v 40A Power Supply](https://www.amazon.co.uk/inShareplus-Universal-Regulated-Switching-Transformer/dp/B08QRCSTG4))

### Software

- :black_medium_square: [RPi RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library to drive HUB75 LED panels with a Raspberry Pi
- :video_game: [PyGame CE](https://www.pyga.me/) Python based 2D graphics and gaming engine
- :penguin: [DietPi](https://dietpi.com/), a minimal lightweight Linux distribution designed for Raspberry Pi devices
- :snake: Python 3.10+, [ECS Pattern](https://github.com/ikvk/ecs_pattern), [Paho MQTT Client](https://pypi.org/project/paho-mqtt/), etc.

## Installation

### RGB LED Matrix Driver

Fetch dependencies submodules:

    git submodule update --init --recursive

Build `rpi-rgb-led-matrix` Python bindings:

    cd lib/rpi-rgb-led-matrix
    make build-python

### Python 3.10

If using Debian Bookworm, you will need to install Python 3.10 as the default 3.9 version will not work. You can add an APT repository to install Python 3.10 packages:

Add the following to `/etc/apt/sources.list` or equivalent:

    deb http://deb.pascalroeleven.nl/python3.10 bullseye-backports main

Install:

    apt update
    apt install python3.10

## Configuration

Project configuration is provided using [Dynaconf](https://www.dynaconf.com/), meaning that configuration can be provided using one or more TOML files, but can also be overridden at runtime using environment variables. For more information, see [`config.py`](./wideboy/config.py).

The provided [`settings.toml`](./settings.toml) details all the available options, but they are all commented out. The preferred method of configuration is to override any settings by creating a `settings.local.toml` and/or a `secrets.toml` (for sensitive values). Both of these files, if they exist, will be used, but should not be stored in source control and are therefore ignored using `.gitignore`.

If using the Docker container, the provided [`docker-compose.yml`](./docker-compose.yml) file will attempt to load environment variables from `./docker.local.env`. An example environment file is provided to copy and modify:

    cp ./docker.env ./docker.local.env

Any configuration value can be applied using environment variables which all start with `WIDEBOY_` and have a flattened uppercase underscore delimited format. Note that each nested level should be separated by double underscore (`__`). For example, the following TOML snippet and the equivalent environment variables:

#### TOML

    [mqtt]
      host = mqtt.local
      user = mqtt
    [paths]
      images_backgrounds = "/images"

#### Environment Variables

    WIDEBOY_MQTT__HOST=mqtt.local
    WIDEBOY_MQTT__USER=mqtt
    WIDEBOY_PATHS__IMAGES_BACKGROUNDS=/images

## Development

Create a Python 3.10+ virtual environment, and install project dependencies:

    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip poetry
    poetry install

## Running

### Docker

There is now an official `arm64` image available in [GHCR](https://github.com/jinglemansweep/wideboy/pkgs/container/wideboy) which should run fine on any modern Raspberry Pi. An example [`docker-compose.yml`](./docker-compose.yml) has been provided which loads it environment variables from `docker.local.env` which needs to be created before starting.

Note that the Docker image requires `privileged` mode and access to `/dev/mem` (for GPIO access):

    cp ./docker.env ./docker.local.env
    docker compose pull
    docker compose up -d

To view logs:

    docker compose logs -f wideboy

### Source

To run the project:

    . venv/bin/activate
    python3 -m wideboy
