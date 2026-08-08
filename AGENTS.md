# AGENTS.md

## Project

768x64 RGB LED matrix dashboard for Raspberry Pi. Python 3.11+, pygame-ce, numpy, pydantic.

## Commands

- **Run**: `python -m wideboy` (emulator by default, `--backend hardware` for Pi)
- **Test**: `pytest`
- **Lint**: `ruff check .`
- **Format**: `ruff format .`

## Architecture

```
src/wideboy/
  __main__.py              # Entry point, async main loop
  config.py                # Pydantic settings models, YAML config loader
  core/
    scene.py               # Scene YAML parsing
    factory.py             # Wires backgrounds + widgets from scene config
    layer.py               # Base Layer (cached surface, z-order, visibility)
  backgrounds/
    base.py                # Background ABC (update + render)
    composite.py           # CompositeBackground for multi-background scenes
    image.py               # Static image background
    slideshow.py           # Image slideshow background
    gif.py                 # Animated GIF background
    procedural/            # numpy-based procedural effects
      _base.py             # Effect base class
      _registry.py         # EFFECTS dict + ProceduralBackground
      _utils.py            # palette_array, sample_palette, draw helpers
      <effect>.py          # One file per effect (plasma.py, tetris.py, etc.)
  widgets/
    base.py                # Widget ABC (extends Layer)
    clock.py               # Digital clock widget
    tile_grid.py           # Home Assistant entity tile grid
  render/
    palette.py             # Palette model + PaletteClock for palette cycling
    text.py                # Bitmap font rendering
    icons.py               # Material Design Icons rendering
    brightness.py          # Brightness manager with scheduled transitions
    image.py               # Image loading and scaling
  services/
    homeassistant.py       # HA WebSocket state polling
    mqtt_hass.py           # MQTT Discovery + remote control commands
  display/
    emulator.py            # pygame window output (dev)
    hardware.py            # rpi-rgb-led-matrix driver (Pi)
    remap.py               # Panel output remapping + test pattern
```

Top-level files:

```
scenes/default.yml         # Scene definition (backgrounds, widgets, HA entities)
settings.yml               # Committed defaults
settings.local.yml         # Local overrides (gitignored)
secrets.yml                # Credentials (gitignored)
palettes.yml               # Palette definitions
deploy.sh                  # rsync to Pi (excludes secrets, local settings, caches)
scripts/                   # Dev scripts (e.g. capture_effects.py for screenshots)
```

## Config

Config deep-merges three YAML files in order:

```
settings.yml  →  settings.local.yml  →  secrets.yml
```

Only `settings.yml` is committed. Pydantic models live in `config.py` — add new fields there. Environment variables override via `WIDEBOY_<SECTION>__<KEY>` (double underscore delimiter).

## Adding a Procedural Effect

1. Create `src/wideboy/backgrounds/procedural/<name>.py`
2. Subclass `Effect` from `._base`. Set `name`, `default_palette`, and `tags`.
3. Implement `__call__(self, t, w, h, palette) -> np.ndarray` returning shape `(h, w, 3)` uint8.
4. Use `palette_array()` and `sample_palette()` from `_utils` to map palette colors to pixel data.
5. Import and register in `_registry.py`: add the import and entry in the `EFFECTS` dict.
6. Run `python scripts/capture_effects.py <name>` to capture the new effect's screenshot into `docs/screenshots/`. Omit the name to regenerate all screenshots. It runs headless (sets `SDL_VIDEODRIVER=dummy`).
7. Update `README.md`:
   - Bump the effect count in three places: the `## Effects` intro line, the Features bullet (`**N procedural effects**`), and the project-layout comment (`procedural (N effects)`).
   - Add a new `### Display Name` section (kept in alphabetical order) following the existing format:

     ```markdown
     ### Display Name

     ![name](docs/screenshots/name.png)

     One-line description. Tags: `tag1`, `tag2`. Palette: `palette`.
     ```

## Adding a Widget

1. Create `src/wideboy/widgets/<name>.py`
2. Subclass `Widget` from `widgets.base` (extends `Layer`).
3. Implement `update(dt)` and `_render(surface)`. The `Layer` base handles dirty-checking and blitting.
4. Wire in `core/factory.py`: add a type case in `build_widgets()`, then configure in `scenes/default.yml`.

## Constraints

- Canvas is **768x64**. All rendering targets this resolution.
- Effects return numpy arrays converted via `pygame.surfarray.make_surface(arr.transpose(1, 0, 2))`.
- Expensive effects (aurora, mandelbrot) render at half resolution and scale up — see `_SCALE_EFFECTS` in `_registry.py`.
- Widgets use cached surfaces via `Layer` — call `mark_dirty()` when content changes to force re-render.
- `deploy.sh <host>` rsyncs to Pi. It copies `settings.yml` but excludes `secrets.yml` and `settings.local.yml`.
