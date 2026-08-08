# Plan: `wideboyng` — 768×64 RGB LED Matrix Dashboard

Status: draft v1 (2026-08-06)

## Overview

New project in `/home/louis/data/dev/wideboyng`. A Python app that renders widgets over
animated backgrounds on 6× 128×64 HUB75 panels (logical **768×64**), driven by a
Pi 4 + Electrodragon v2 HAT (3 outputs, 2 panels chained per output) via the
`rpi-rgb-led-matrix` Python bindings, with `RGBMatrixEmulator` for local dev/testing.

Ports the clock, Home Assistant tile grid, and image slideshow from the existing
`wideboy` project (`/home/louis/data/dev/wideboy`), drops ECS/MQTT in favour of a simple
layer system, and adds high-performance animated backgrounds (procedural and GIF in
v1, video as a fast-follow).

## Decisions confirmed with user

- Rendering engine: **pygame-ce** (existing widgets are pygame-based)
- Architecture: **simple ordered layers** (ECS dropped)
- Dev/test: **RGBMatrixEmulator** (browser adapter default)
- Hardware: **Pi 4 + Electrodragon v2**, `gpio_mapping=regular`
- Panels: 6× 128×64 arranged horizontally → logical 768×64
- Wiring: 3 parallel outputs, 2 chained panels each; output order (left→right vs
  right→left) **unknown** → configurable `output_order` + test pattern
- Tooling: **uv**
- Home Assistant: **WebSocket `subscribe_trigger`** for real-time updates of the <20
  displayed entities (server-side filtering); per-entity REST to seed + as fallback.
  No bulk `/api/states`, no MQTT statestream config.
- Backgrounds: image slideshow + procedural + GIF in v1; **video fast-follow**
- Config: **pydantic-settings** (YAML sources + `WIDEBOYNG_` env overrides)
- Tile grid cells: **YAML-driven** (entity_id, icon, label template, colors in scene YAML)
- v1 scope: clock widget, HA tile grid, slideshow background, YAML scenes
  (MQTT/HA remote control deferred; video backgrounds deferred)

## Key design decisions

### 1. Panel geometry remap (the critical bit)

With `rows=64, cols=128, chain_length=2, parallel=3`, the library's native framebuffer
is **256×192** (chains extend horizontally, parallel outputs stack vertically) — not
768×64. Solution:

- App always renders a logical **768×64** pygame surface.
- The hardware backend splits it into three 256×64 segments and stacks them into the
  256×192 physical layout via a numpy reshape/transpose (~µs per frame):

  ```python
  # frame: np.ndarray shape (64, 768, 3), order: list of segment indices e.g. [0,1,2]
  segs = frame.reshape(64, 3, 256, 3)  # (rows, segment, cols, rgb)
  physical = segs[:, order].transpose(1, 0, 2, 3).reshape(192, 256, 3)
  ```

- `output_order` config: `[0,1,2]` (outputs left→right) or `[2,1,0]` (right→left).
- `--test-pattern` mode draws labelled colour bars per segment to verify wiring on real
  hardware before trusting the mapping.

The emulator backend instead configures `rows=64, cols=128, chain_length=6` → a true
768×64 window, so dev always shows the intended layout.

### 2. Display abstraction

```
Display.present(pygame.Surface)
├── EmulatorDisplay   — RGBMatrixEmulator, browser adapter :8888 (headless-friendly)
└── HardwareDisplay   — lazy `import rgbmatrix` (Pi-only dep), full driver options
```

Both use the fast path: `CreateFrameCanvas()` → `SetImage(PIL)` → `SwapOnVSync()`
(same pattern as existing `wideboy.systems.display.SysDisplay`). Selection via
`--backend emulator|hardware`.

Emulator notes:
- Configured via `emulator_config.json` in CWD (pixel_size ~8 for 768-wide window).
- Always use frame-canvas path; the emulator redraws the whole screen on every
  direct `matrix.SetPixel`/`SetImage` call.
- pygame surface → PIL conversion: `pygame.image.tostring` + `Image.frombytes` (as in
  existing `surface_to_led_matrix`).

### 3. Rendering core (ECS dropped)

- pygame-ce, offscreen 768×64 surface (`SDL_VIDEODRIVER=dummy` on hardware).
- `Layer` base: position, z-order, visibility, `update(dt)` / `render(surface)`,
  dirty-cached surfaces (widgets re-render only on change, blit cached surface
  every frame).
- Scene = one background + ordered widget layers, defined in YAML
  (same shape as `wideboy/scenes/default.yml`).
- FPS-limited main loop (default 30, configurable).

### 4. Backgrounds (pluggable registry)

| Type | Implementation | v1 |
|---|---|---|
| `image` | static image scaled to 768×64 | yes |
| `slideshow` | port of `SlideshowSprite` incl. fade/wipe/fold/bleed transitions | yes |
| `gif` | PIL `ImageSequence` pre-decode → surfaces, per-frame durations, loop | yes |
| `procedural` | numpy effects with precomputed coordinate meshes: plasma, palette/gradient scroll, starfield, waves — 768×64 is only ~49K px, comfortably 30–60fps on Pi 4 | yes |
| `video` | ffmpeg subprocess → raw RGB pipe → numpy → surface; decoder thread with latest-frame queue | **fast-follow** |

Registry pattern: each background type registers under a name; scene YAML selects by
`type:` plus per-type `settings:`.

### 5. Widgets

- **`clock`** — time + date text, ported `render_text` (outline rendering), fonts copied
  from wideboy (`white-rabbit.ttf`, `bitstream-vera.ttf`), 24h option.
- **`tile_grid`** — port of `TileGrid`/`TileGridCell`/`TileGridColumn` rendering
  (FontAwesome icons via `fontawesome-solid.otf`, collapse animations), fed by the HA
  service (WebSocket push) instead of MQTT statestream.
  **Cells are YAML-driven**: each tile is declared in the scene file with `entity_id`,
  icon (FontAwesome name/codepoint), label template (`"{value}°C"`), colors, and
  visibility rules. No per-tile Python subclasses. A generic `Tile` model maps the
  state value (on/off/number/string) onto the configured presentation.

### 6. Home Assistant service (WebSocket-first, real-time)

User has a very large HA registry but displays <20 entities and wants near-real-time
(<5s) updates. Bulk REST polling is too expensive and too slow. Revised approach:

- **Primary: WebSocket `subscribe_trigger`.** One WS connection (long-lived token).
  Send `subscribe_trigger` with a `state` platform trigger listing the configured
  `entity_id`s. HA filters **server-side** and pushes an event only when one of those
  entities changes → sub-second updates, no polling, no MQTT config. (This is wideboy's
  `SysHomeAssistantWebsocket` idea, but actually wired to the configured entity list —
  wideboy's was left with an empty list so it never subscribed.)
- **Seed on (re)connect:** cheap per-entity REST `GET /api/states/<id>` for the <20
  entities to populate initial state; never the bulk `/api/states`.
- **Fallback:** if websockets are disabled/unavailable, per-entity REST polling on an
  interval (default 5s). Configurable.
- Runs in a background thread; updates a thread-safe snapshot (main loop reads a
  consistent dict). Tile cells mark dirty on change. Reconnect with backoff; on failure
  keep last good snapshot and render `unavailable` styling rather than crashing.
- Config: host/port/token via `secrets.yml` or env vars.

### 6b. Threading & performance model (GIL-aware)

Target 30fps on Pi 4. The GIL is not the bottleneck because expensive per-frame work
lives in C extensions that release it:

- Procedural backgrounds = vectorized numpy (releases GIL, multicore).
- HA websocket = socket I/O (releases GIL).
- Panel refresh = rgbmatrix C library runs on its own internal thread/core.
- Text/icon rendering = dirty-cached, re-rendered only on state change (not per frame).

Design rule: **worker threads produce data (numpy arrays / bytes); the main thread owns
all pygame surfaces** (pygame is not thread-safe for surface ops).

Threads:
1. **Main/render thread** — composite + display push, 30fps, owns pygame surfaces.
2. **HA websocket thread** — I/O-bound; pushes state into a thread-safe snapshot.
3. **Decoder worker(s)** — GIF pre-decode at load (video in fast-follow); hand frames
   to the main thread.
4. **Optional core isolation** — pin render thread to a dedicated core
   (`isolcpus`/affinity) per rpi-rgb-led-matrix guidance to avoid flicker from
   scheduling jitter.

If a background proves pure-Python-heavy, precompute its frames in a worker thread —
unlikely to be needed at 768×64 (~49K px) with numpy.

### 7. Tooling

- **uv** project. Deps: `pygame-ce`, `numpy`, `pillow`, `pyyaml`, `pydantic`,
  `pydantic-settings`, `requests`, `websocket-client` (sync client, matches the
  dedicated-thread model and wideboy's existing dep).
  Dev extras: `RGBMatrixEmulator`, `pytest`, `ruff`.
- **Config via `pydantic-settings`**: typed `Settings` models with validation. Sources,
  in increasing precedence: defaults → `settings.yml` → `settings.local.yml` →
  `secrets.yml` → environment variables (prefix `WIDEBOYNG_`, nested via `__`, e.g.
  `WIDEBOYNG_DISPLAY__MATRIX__BRIGHTNESS=50`). This replaces dynaconf while keeping
  the env-override behaviour wideboy relied on for systemd/Docker.
- `rpi-rgb-led-matrix` installed on the Pi only
  (`uv pip install git+https://github.com/hzeller/rpi-rgb-led-matrix`, needs
  `python3-dev`/`cython3`/`gcc`), lazy-imported so dev machines never build it.
- systemd unit for production (run as root for GPIO timing; library drops privileges
  after init).

## Repo layout

```
wideboyng/
├── pyproject.toml, README.md, .gitignore
├── settings.yml, settings.local.yml.example, secrets.yml.example
├── emulator_config.json          # adapter/pixel_size etc.
├── scenes/default.yml
├── fonts/                        # copied from wideboy (white-rabbit, bitstream-vera, fontawesome-solid)
├── assets/backgrounds/           # images, gifs, videos
├── systemd/wideboyng.service
├── src/wideboyng/
│   ├── __main__.py               # argparse, main loop
│   ├── config.py                 # pydantic-settings models + YAML/env loading
│   ├── display/{base,emulator,hardware,remap}.py
│   ├── core/{scene,layer}.py
│   ├── backgrounds/{base,image,slideshow,gif}.py + procedural/   # video.py fast-follow
│   ├── widgets/{base,clock,tile_grid}.py
│   ├── services/homeassistant.py
│   └── render/{text,icons}.py
└── tests/
```

## Implementation order

1. Scaffold: uv project, pydantic-settings config, logging, entrypoint
2. Display abstraction + emulator backend + test pattern → verify visually in browser
3. Scene/layer core + main loop
4. Backgrounds: image, slideshow (port), procedural effects
5. GIF backgrounds
6. Text helpers + clock widget
7. HA service (WebSocket subscribe_trigger + REST seed/fallback) + YAML-driven tile grid (port)
8. Default scene YAML wiring everything together
9. Hardware backend + numpy remap + unit tests
10. Deploy docs: README, systemd unit, Pi setup notes

### Fast-follow (post-v1)

- Video backgrounds (ffmpeg pipe + decoder thread)
- MQTT / Home Assistant remote control (power/brightness, scene select, intervals)

## Verification

- `pytest`: remap correctness for both output orders, scene parsing, config validation
- `ruff` lint
- Manual: run with emulator (browser adapter) and inspect animations/widgets
- On Pi: `--test-pattern` to confirm output→segment mapping, then tweak
  `output_order`/`row_addr_type` as needed

## Risks / open items

- Panel addressing type (ABCDE vs ABC shift-register) unknown — expose
  `row_addr_type`/`multiplexing`/`panel_type` in config; may need experimentation
  on hardware.
- Parallel-output stacking order assumption (chain 0 = top) — covered by test pattern
  + configurable order.
- Video decode budget on Pi 4 (deferred to fast-follow) — keep content at 768×64,
  cap ~24–30fps, off-thread decoding.
- YAML-driven tiles are more upfront work than porting Python classes, but make the
  dashboard config-only; icon set limited to FontAwesome codepoints we map by name.

## Reference: existing wideboy code to port

| Source (wideboy) | Target (wideboyng) |
|---|---|
| `wideboy/systems/display.py` (SysDisplay, surface_to_led_matrix) | `display/emulator.py`, `display/hardware.py` |
| `wideboy/sprites/slideshow/__init__.py` (transitions) | `backgrounds/slideshow.py` |
| `wideboy/sprites/graphics.py` / `sprites/tile_grid/helpers.py` (render_text, render_icon) | `render/text.py`, `render/icons.py` |
| `wideboy/sprites/text/__init__.py` | `widgets/clock.py` |
| `wideboy/sprites/tile_grid/__init__.py` | `widgets/tile_grid.py` (rendering ported; cell defs become YAML-driven) |
| `wideboy/systems/homeassistant.py` (websocket) | `services/homeassistant.py` — port + fix: actually subscribe to the configured entity_ids (WebSocket `subscribe_trigger`), add REST seed/reconnect/fallback |
| `wideboy/config.py` (dynaconf validators) | `config.py` (pydantic-settings models) |
| `scenes/default.yml` | `scenes/default.yml` |
| `fonts/*` | `fonts/*` |
