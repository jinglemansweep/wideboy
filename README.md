# WideBoy

<img src="docs/images/logo-new.png" width="50%" alt="WideBoy Logo">

768x64 RGB LED matrix dashboard for Raspberry Pi.

Drives 6x 128x64 HUB75 panels (logical 768x64) via a Pi 4 + Electrodragon v2 HAT.
Displays a clock and Home Assistant entity tile grid over animated procedural backgrounds.

## Documentation

- [Installation](docs/install.md) -- Pi setup, rpi-rgb-led-matrix build, systemd, wiring
- [Configuration](docs/config.md) -- settings reference, scene format, MQTT entities

## Effects

24 procedural background effects with tag-based selection and auto-rotation.

### Airwolf

![airwolf](docs/screenshots/airwolf.png)

Airwolf helicopter fly-by. Tags: `nostalgic`, `energetic`. Palette: `mono`.

### Asteroids

![asteroids](docs/screenshots/asteroids.png)

Retro vector asteroids game. Tags: `game`, `retro`, `energetic`. Palette: `mono`.

### Aurora

![aurora](docs/screenshots/aurora.png)

Undulating aurora borealis bands. Tags: `abstract`, `calm`. Palette: `ocean`.

### Boids

![boids](docs/screenshots/boids.png)

Flocking boids simulation. Tags: `nature`, `calm`. Palette: `neon`.

### Breakout

![breakout](docs/screenshots/breakout.png)

Paddle-and-ball brick breaker. Tags: `game`, `retro`, `energetic`. Palette: `neon`.

### Bubbles

![bubbles](docs/screenshots/bubbles.png)

Rising iridescent bubbles. Tags: `particle`, `calm`. Palette: `ocean`.

### Cityscape

![cityscape](docs/screenshots/cityscape.png)

Procedural city skyline. Tags: `nostalgic`, `calm`. Palette: `neon`.

### Conveyor

![conveyor](docs/screenshots/conveyor.png)

Scrolling conveyor belt. Tags: `linear`, `retro`. Palette: `neon`.

### Equalizer

![equalizer](docs/screenshots/equalizer.png)

Audio spectrum bar visualiser. Tags: `retro`, `energetic`. Palette: `neon`.

### Flappy

![flappy](docs/screenshots/flappy.png)

AI-controlled flappy bird with organic movement. Tags: `game`, `retro`. Palette: `neon`.

### Gradient

![gradient](docs/screenshots/gradient.png)

Smooth animated colour gradient. Tags: `abstract`, `calm`. Palette: `ocean`.

### Life

![life](docs/screenshots/life.png)

Conway's Game of Life cellular automaton. Tags: `abstract`, `calm`. Palette: `neon`.

### Lightning

![lightning](docs/screenshots/lightning.png)

Branching lightning bolts. Tags: `energetic`, `dark`. Palette: `neon`.

### Mandelbrot

![mandelbrot](docs/screenshots/mandelbrot.png)

Animated Mandelbrot zoom. Tags: `abstract`, `geometric`. Palette: `sunset`.

### Matrix Rain

![matrix](docs/screenshots/matrix.png)

Falling green code rain. Tags: `retro`, `dark`. Palette: `forest`.

### Plasma

![plasma](docs/screenshots/plasma.png)

Classic plasma colour cycling. Tags: `abstract`, `calm`. Palette: `neon`.

### Rings

![rings](docs/screenshots/rings.png)

Expanding concentric ring ripples. Tags: `geometric`, `calm`. Palette: `sunset`.

### Scanlines

![scanlines](docs/screenshots/scanlines.png)

CRT-style scanline sweep. Tags: `retro`, `dark`. Palette: `neon`.

### Slosh

![slosh](docs/screenshots/slosh.png)

Fluid sloshing liquid simulation. Tags: `liquid`, `calm`. Palette: `ocean`.

### Snow

![snow](docs/screenshots/snow.png)

Falling snowflake particles. Tags: `particle`, `calm`. Palette: `mono`.

### Starfield

![starfield](docs/screenshots/starfield.png)

3D star warp fly-through. Tags: `particle`, `calm`, `dark`. Palette: `mono`.

### Tetris

![tetris](docs/screenshots/tetris.png)

AI-controlled falling Tetris blocks. Tags: `game`, `retro`. Palette: `neon`.

### Traffic

![traffic](docs/screenshots/traffic.png)

Animated traffic jam scene. Tags: `linear`, `energetic`. Palette: `neon`.

### Waves

![waves](docs/screenshots/waves.png)

Sine-wave interference patterns. Tags: `abstract`, `calm`. Palette: `forest`.

## Features

- **24 procedural effects** with tag-based selection and auto-rotation
- **Custom tags** assignable to any effect via settings YAML for personalised groupings
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
    ├── backgrounds/          # image, slideshow, gif, procedural (24 effects)
    ├── widgets/              # clock, tile_grid
    ├── services/             # HA WebSocket + MQTT/HASS
    └── render/               # text, icons, palette, brightness
```
