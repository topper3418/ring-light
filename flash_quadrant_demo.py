import argparse
import time

import board

from ring_led import RingLed


def parse_color(color_text):
    parts = color_text.split(",")
    if len(parts) != 3:
        raise ValueError("Color must be in R,G,B format, for example 0,0,255")
    color = tuple(int(value.strip()) for value in parts)
    if any(value < 0 or value > 255 for value in color):
        raise ValueError("Each color component must be between 0 and 255")
    return color


def main():
    parser = argparse.ArgumentParser(description="Flash one ring quadrant for setup verification")
    parser.add_argument("--side", type=int, required=True, choices=[1, 2, 3, 4], help="Quadrant: 1=top, 2=right, 3=bottom, 4=left")
    parser.add_argument("--flipped", action="store_true", help="Flip the ring orientation")
    parser.add_argument("--color", default="0,0,255", help="Flash color as R,G,B")
    parser.add_argument("--interval", type=float, default=0.25, help="Delay between flashes in seconds")
    args = parser.parse_args()

    color = parse_color(args.color)
    ring = RingLed(board.MOSI, flipped=args.flipped, pixel_count=24, brightness=0.2)

    print(f"Flashing side {args.side}: 1=top, 2=right, 3=bottom, 4=left")
    print("Press Ctrl+C to stop")

    try:
        while True:
            ring.flash_quadrant(args.side, color)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        ring.clear()


if __name__ == "__main__":
    main()
