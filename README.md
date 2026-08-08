# wideboy

768x64 RGB LED matrix dashboard for Raspberry Pi.

Drives 6x 128x64 HUB75 panels (logical 768x64) via a Pi 4 + Electrodragon v2 HAT.
Displays a clock and Home Assistant entity tile grid over animated procedural backgrounds.

## Screenshots

| | | |
|---|---|---|
| **Plasma**<br>![plasma](docs/screenshots/plasma.png) | **Matrix Rain**<br>![matrix](docs/screenshots/matrix.png) | **Starfield**<br>![starfield](docs/screenshots/starfield.png) |
| Classic plasma colour cycling | Falling green code rain | 3D star warp fly-through |
| **Aurora**<br>![aurora](docs/screenshots/aurora.png) | **Breakout**<br>![breakout](docs/screenshots/breakout.png) | **Bubbles**<br>![bubbles](docs/screenshots/bubbles.png) |
| Undulating aurora borealis bands | Paddle-and-ball brick breaker | Rising iridescent bubbles |
| **Asteroids**<br>![asteroids](docs/screenshots/asteroids.png) | **Traffic**<br>![traffic](docs/screenshots/traffic.png) | **Slosh**<br>![slosh](docs/screenshots/slosh.png) |
| Retro vector asteroids game | Animated traffic jam scene | Fluid sloshing liquid sim |
| **Equalizer**<br>![equalizer](docs/screenshots/equalizer.png) | **Lightning**<br>![lightning](docs/screenshots/lightning.png) | **Airwolf**<br>![airwolf](docs/screenshots/airwolf.png) |
| Audio spectrum bar visualiser | Branching lightning bolts | Airwolf helicopter fly-by |
| **Snow**<br>![snow](docs/screenshots/snow.png) | **Waves**<br>![waves](docs/screenshots/waves.png) | **Mandelbrot**<br>![mandelbrot](docs/screenshots/mandelbrot.png) |
| Falling snowflake particles | Sine-wave interference patterns | Animated Mandelbrot zoom |
| **Rings**<br>![rings](docs/screenshots/rings.png) | **Tetris**<br>![tetris](docs/screenshots/tetris.png) | **Cityscape**<br>![cityscape](docs/screenshots/cityscape.png) |
| Expanding concentric ring ripples | Falling Tetris blocks | Procedural city skyline |
| **Boids**<br>![boids](docs/screenshots/boids.png) | **Scanlines**<br>![scanlines](docs/screenshots/scanlines.png) | **Conveyor**<br>![conveyor](docs/screenshots/conveyor.png) |
| Flocking boids simulation | CRT-style scanline sweep | Scrolling conveyor belt |
| **Gradient**<br>![gradient](docs/screenshots/gradient.png) | | |
| Smooth animated colour gradient | | |

## Features

- **22 procedural effects** with tag-based selection and auto-rotation
- **Home Assistant integration** via WebSocket (entity state) and MQTT (control)
- **Live control** from HA: on/off, brightness, effect, palette, tag filter, scene
- **Scene-based config** in YAML with layered settings and env var overrides
- **Emulator mode** for local development (no Pi required)
- **Smooth transitions** between effects (1-second crossfade each minute)

## Quick start

```bash
uv venv && uv pip install -e ".[dev]"
python -m wideboy                            # emulator at http://localhost:8888
python -m wideboy --test-pattern             # test pattern (verify panel wiring)
```

Requires Python 3.11+. The emulator uses [RGBMatrixEmulator](https://github.com/dfirestone/RGBMatrixEmulator).

## Documentation

- [Installation](docs/install.md) -- Pi setup, rpi-rgb-led-matrix build, systemd, wiring
- [Configuration](docs/config.md) -- settings reference, scene format, MQTT entities

## Project layout

```
wideboy/
├── settings.yml              # default config
├── secrets.yml.example       # template for HA credentials
├── scenes/default.yml        # active scene
├── palettes.yml              # colour palettes
├── fonts/                    # white-rabbit, bitstream-vera, fontawesome-solid
├── assets/backgrounds/       # user-provided slideshow images
├── systemd/                  # systemd service unit
├── scripts/                  # utility scripts (screenshot capture)
└── src/wideboy/
    ├── __main__.py           # entrypoint + main loop
    ├── config.py             # pydantic-settings models
    ├── display/              # emulator + hardware backends + remap
    ├── core/                 # scene loader, factory, layer base
    ├── backgrounds/          # image, slideshow, gif, procedural (22 effects)
    ├── widgets/              # clock, tile_grid
    ├── services/             # HA WebSocket + MQTT/HASS
    └── render/               # text, icons, palette, brightness
```
