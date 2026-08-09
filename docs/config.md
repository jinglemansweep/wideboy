# Configuration

## Settings files

Settings are loaded in precedence order, with later files overriding earlier ones:

1. `settings.yml` -- defaults (committed)
2. `settings.local.yml` -- local overrides (gitignored)
3. `secrets.yml` -- sensitive values (gitignored)
4. `WIDEBOY_*` env vars (nested via `__`, e.g. `WIDEBOY_DISPLAY__MATRIX__BRIGHTNESS=50`)

## Key settings

| Section | Key | Default | Description |
|---|---|---|---|
| `general.log_level` | `info` | `debug`, `info`, `warning`, `error` |
| `general.fps` | `30` | Target frame rate |
| `display.canvas.width` | `768` | Logical display width |
| `display.canvas.height` | `64` | Logical display height |
| `display.matrix.enabled` | `false` | Enable hardware matrix (disable for emulator) |
| `display.matrix.brightness` | `50` | 0-100 |
| `display.matrix.driver.chain` | `2` | Panels per chain |
| `display.matrix.driver.parallel` | `3` | Number of parallel chains |
| `display.matrix.remap.output_order` | `[0, 1, 2]` | Remap output order |
| `homeassistant.host` | `""` | HA hostname or IP |
| `homeassistant.port` | `8123` | HA port |
| `homeassistant.token` | `""` | Long-lived access token |
| `homeassistant.ssl` | `false` | Use HTTPS |
| `mqtt.enabled` | `false` | Enable MQTT |
| `mqtt.host` | `""` | MQTT broker hostname |
| `mqtt.port` | `1883` | MQTT broker port |
| `mqtt.username` | `""` | MQTT username |
| `mqtt.password` | `""` | MQTT password (prefer `secrets.yml`) |
| `mqtt.device_id` | `wideboy` | MQTT device identifier |
| `mqtt.device_name` | `Wideboy LED Display` | HA device name |
| `scenes.file` | `scenes/default.yml` | Active scene file |
| `paths.backgrounds` | `assets/backgrounds` | Slideshow image directory |
| `paths.fonts` | `fonts` | Font directory |
| `brightness.background.default` | `1.0` | Background brightness multiplier |
| `brightness.foreground.default` | `1.0` | Foreground brightness multiplier |
| `effect_tags` | `{}` | Extra tags per effect (see [Custom effect tags](#custom-effect-tags)) |

## Scene format

Scenes are defined in YAML files under `scenes/`.

### Metadata

```yaml
metadata:
  name: default
  description: Default dashboard scene
```

### Palette

Scenes can define a default palette and fade duration for transitions between palettes:

```yaml
palette:
  default: neon
  fade_seconds: 3.0
```

Palettes are defined in `palettes.yml`:

```yaml
palettes:
  neon:
    primary: [0, 220, 255]
    secondary: [255, 0, 200]
    accent: [255, 220, 0]
    highlight: [255, 255, 255]
    dim: [10, 10, 40]
```

Each palette has five colour channels used by effects.

### Backgrounds

Multiple backgrounds can be listed. They rotate every minute with a 1-second crossfade.

#### Procedural effects (tag-based)

```yaml
backgrounds:
  - type: procedural
    tags: []          # empty = all effects
```

With tag filtering (OR logic -- any matching tag includes the effect):

```yaml
backgrounds:
  - type: procedural
    tags: [retro, game]
```

#### Procedural effects (explicit)

```yaml
backgrounds:
  - type: procedural
    settings:
      effect: plasma
      speed: 1.0
      palette: sunset
```

#### Available tags

`abstract`, `calm`, `dark`, `energetic`, `game`, `geometric`, `linear`,
`liquid`, `nature`, `nostalgic`, `particle`, `retro`

Custom tags can be added via the [`effect_tags`](#custom-effect-tags) setting.

#### Available effects (29)

| Effect | Tags | Default palette |
|--------|------|-----------------|
| airwolf | energetic, nostalgic | mono |
| asteroids | energetic, game, retro | mono |
| aurora | abstract, calm, dark | ocean |
| boids | calm, nature, particle | neon |
| breakout | energetic, game, retro | neon |
| bubbles | calm, particle | ocean |
| cityscape | dark, energetic, nostalgic | neon |
| conveyor | linear, retro | neon |
| equalizer | energetic, retro | neon |
| flappy | game, retro | neon |
| gradient | abstract, calm | ocean |
| life | abstract, calm, geometric, retro | neon |
| lightning | dark, energetic | neon |
| mandelbrot | abstract, geometric | sunset |
| matrix | dark, retro | forest |
| outrun | energetic, game, nostalgic, retro | sunset |
| plasma | abstract, calm | neon |
| polyhedrons | dark, geometric, particle | neon |
| primes | calm, dark, geometric | neon |
| rings | calm, geometric | sunset |
| scanlines | dark, retro | neon |
| solar | calm, dark, nature | mono |
| slosh | calm, liquid | ocean |
| snow | calm, particle | mono |
| starfield | calm, dark, particle | mono |
| strobe | geometric, linear, retro | mono |
| tetris | game, retro | neon |
| traffic | energetic, linear | neon |
| waves | abstract, calm | forest |

#### Other background types

```yaml
# Static image
backgrounds:
  - type: image
    settings:
      path: assets/backgrounds/hero.png

# Slideshow (random images from directory)
backgrounds:
  - type: slideshow
    settings:
      path: assets/backgrounds
      interval: 60
      transition: fade       # fade | wipe | none
      transition_speed: 8

# Animated GIF
backgrounds:
  - type: gif
    settings:
      path: assets/backgrounds/anim.gif
```

### Custom effect tags

The `effect_tags` setting lets you add your own tags to any effect. These
merge with the effect's built-in tags and are available everywhere tags
are used -- the HASS tag dropdown, tag-filtered rotation, and
`get_effects_by_tags` / `get_all_tags` APIs.

```yaml
effect_tags:
  plasma: [evening]
  rings: [evening]
  starfield: [evening]
  flappy: [fun, loud]
```

Selecting the `evening` tag from HASS then rotates only those three effects.

Tags specified in later settings files replace the per-effect list (they
are not concatenated):

```yaml
# settings.yml
effect_tags:
  plasma: [evening]

# settings.local.yml
effect_tags:
  plasma: [morning]    # result: [morning], not [evening, morning]
```

### Widgets

#### Clock

```yaml
widgets:
  - type: clock
    position: [2, 0]
    anchor: top-right
    settings:
      time_format: "%H:%M"
      date_format: "%a %d %b"
      size_time: 20
      size_date: 10
      font_time: fonts/white-rabbit.ttf
      font_date: fonts/white-rabbit.ttf
```

#### Tile grid

```yaml
widgets:
  - type: tile_grid
    position: [128, 0]
    anchor: top-right
    settings:
      columns:
        - - entity_id: sensor.temperature
            icon: 0xF015          # FontAwesome codepoint
            visible_when: defined
            label_template: "{value}°"
          - entity_id: binary_sensor.door
            icon: 0xF52A
            label: "Front"
            visible_when: "on"
            color_bg: [64, 0, 0, 255]
            color_icon_bg: [255, 0, 0, 255]
```

Tile fields:

| Field | Description |
|-------|-------------|
| `entity_id` | Home Assistant entity (required) |
| `icon` | FontAwesome codepoint (hex) |
| `label` | Static label text |
| `label_template` | Format string: `{value}`, `{value:.1f}`, etc. |
| `visible_when` | Condition for showing the tile (see below) |
| `visible_attribute` | Attribute to check (for `days_until`) |
| `threshold` | Numeric threshold for `below`/`above`/`days_until` |
| `color_bg` | Background colour when condition is met |
| `color_icon_bg` | Icon background colour when condition is met |
| `color_bg_alert` | Background colour when threshold is crossed |
| `color_icon_bg_alert` | Icon background colour when threshold is crossed |

Visibility conditions:

| Condition | Shows when |
|-----------|-----------|
| `always` | Always visible |
| `defined` | State is not `unavailable`/`unknown` |
| `on` | State is `on`/`true`/`open` |
| `off` | State is `off`/`false`/`closed` |
| `below` | Numeric value < `threshold` |
| `above` | Numeric value > `threshold` |
| `days_until` | Days until `timestamp` attribute < `threshold` |

### Home Assistant entities

List entities to subscribe to via WebSocket (auto-collected from tiles if omitted):

```yaml
homeassistant:
  entities:
    - sensor.temperature
    - binary_sensor.door
```

### Widget positioning

| Anchor | Position offset from |
|--------|---------------------|
| `top-left` (default) | Top-left corner |
| `top-right` | Top-right corner |
| `bottom-left` | Bottom-left corner |
| `bottom-right` | Bottom-right corner |

## MQTT / Home Assistant control

When MQTT is enabled, wideboy publishes Home Assistant discovery entities:

| Entity | Type | Description |
|--------|------|-------------|
| `light` | Light | Master on/off + background brightness |
| `fg_brightness` | Number | Foreground brightness (0-100%) |
| `effect_speed` | Number | Effect animation speed (0.1-5.0) |
| `scene` | Select | Switch scene file (reloads) |
| `effect` | Select | Lock to specific effect, or `auto` to resume rotation |
| `tag` | Select | Filter effects by tag, or `all` |
| `palette` | Select | Override palette for current effect |

Topics follow the pattern `{device_id}/{entity}/set` for commands and
`{device_id}/{entity}/state` for state updates.

Discovery is published to `{discovery_prefix}/component/{device_id}/{entity}/config`.

### Behaviour

- Selecting an **effect** locks rotation to that effect until `auto` is selected or the
  scene is reloaded.
- Selecting a **tag** filters the rotation pool and unlocks any locked effect.
- Selecting a **palette** applies to the currently active effect only.
- **Scene** changes reload the full scene file and reset all overrides.
