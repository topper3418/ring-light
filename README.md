# Ring LED Project

`RingLed` is a small Python class for a 24-pixel NeoPixel ring on Raspberry Pi.

## Features

- `flash_quadrant(side, color)`
- `display_ping(polar_coordinate_array)`
- `spin_ring(color, speed)`
- `flipped=True` mode that maps 12 o'clock to 6 o'clock while keeping 3 and 9 fixed

## Wiring (SPI mode, no sudo)

- Ring DIN -> Raspberry Pi GPIO10 (MOSI), physical pin 19
- Ring 5V -> external 5V supply
- Ring GND -> external GND and Raspberry Pi GND (shared ground)

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Spinner Demo

```bash
python spin_ring.py
```

## API Example

```python
import board
from ring_led import RingLed

ring = RingLed(board.MOSI, flipped=False, pixel_count=24, brightness=0.2)

# Flash top quadrant blue
ring.flash_quadrant(1, (0, 0, 255))

# Show ping blobs: [angle_degrees, distance_0_to_10]
ring.display_ping([
    [0, 10],
    [90, 6],
    [210, 2],
])

# Spin ring forever (Ctrl+C to stop)
ring.spin_ring((0, 0, 255), speed=20)
```

## Notes

- Distance color mapping in `display_ping`: `0 -> red`, `10 -> blue`, linear gradient in between.
- Blob behavior: each ping blends into adjacent pixels with a soft falloff.
- If SPI is not available, enable it in `raspi-config` and ensure your user is in the `spi` group.
