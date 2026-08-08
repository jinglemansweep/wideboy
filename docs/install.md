# Installation

## Local development (emulator)

```bash
uv venv && uv pip install -e ".[dev]"
python -m wideboy
```

The emulator opens a browser window at http://localhost:8888 showing the 768x64 display.
Requires Python 3.11+.

## Raspberry Pi installation

### 1. System packages

```bash
sudo apt install git python3-dev g++ python3-setuptools python3-cython3 \
    libjpeg-dev zlib1g-dev
```

- `g++` -- native C++ compiler (do not use `aarch64-linux-gnu-g++`)
- `python3-setuptools` / `python3-cython3` -- required to build rpi-rgb-led-matrix

### 2. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env
```

### 3. Clone the project

```bash
git clone https://github.com/jinglemansweep/wideboy.git /opt/wideboy
cd /opt/wideboy
```

### 4. Create venv and install dependencies

```bash
uv venv && uv pip install -e .
```

### 5. Build and install rpi-rgb-led-matrix

The Python bindings are built via CMake and installed with uv. Pillow's internal C
header (`Imaging.h`) is required at build time but not shipped with pip wheels.

```bash
cd /opt
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git

# Pillow's internal C headers -- needed by the rgbmatrix shim but not installed by pip
for f in Imaging.h ImPlatform.h Mode.h Arrow.h ImagingUtils.h; do
  curl -sL "https://raw.githubusercontent.com/python-pillow/Pillow/main/src/libImaging/$f" \
      -o /usr/local/include/$f
done

cd /opt/wideboy
CXX=g++ uv pip install /opt/rpi-rgb-led-matrix
```

> **Note:** If your shell sets `CXX=aarch64-linux-gnu-g++` (cross-compiler), unset it
> first: `unset CXX`. The build must use the native `g++`.

### 6. Configure

Copy and edit the secrets file with your Home Assistant details:

```bash
cp secrets.yml.example secrets.yml
```

Edit `secrets.yml`:

```yaml
homeassistant:
  host: hass.local
  port: 8123
  token: YOUR_LONG_LIVED_ACCESS_TOKEN
```

Generate the token in Home Assistant: **Profile > Security > Long-Lived Access Tokens**.

Edit `scenes/default.yml` to add your HA entities to the tile grid (each `entity_id` is
auto-subscribed via WebSocket).

### 7. Verify wiring

```bash
sudo .venv/bin/python -m wideboy --backend hardware --test-pattern
```

This draws labelled colour bars per segment. If segments are swapped or reversed, edit
`settings.yml`:

```yaml
display:
  matrix:
    remap:
      output_order: [0, 1, 2]   # try [2, 1, 0] if reversed
```

You may also need to tweak these hardware-specific values (panel-dependent):

| Setting | Typical values | Notes |
|---|---|---|
| `row_addr_type` | 0 (ABCDE) or 1 (ABC shift-register) | Experiment if rows are garbled |
| `multiplexing` | 0 | Only for multiplexed panels |
| `panel_type` | `""` or `"FM6126A"` | Some panels need init sequence |

### 8. Run

```bash
sudo .venv/bin/python -m wideboy --backend hardware
```

Run as root for GPIO timing. The library drops privileges after init
(`no_drop_privs: true` in `settings.yml`).

### 9. Systemd service (auto-start on boot)

```bash
sudo cp systemd/wideboy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wideboy
```

The service sets `SDL_VIDEODRIVER=dummy` for headless operation and restarts on failure.

## Deployment

For quick syncs to a Pi without git:

```bash
bash deploy.sh pi@192.168.1.100            # syncs to ~/wideboy
bash deploy.sh pi@192.168.1.100 /opt/wideboy
```

This uses rsync and excludes `.venv/`, `__pycache__/`, `secrets.yml`, and other
development files.
