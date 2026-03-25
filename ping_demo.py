import argparse
import time

import board

from ring_led import RingLed


def main():
    parser = argparse.ArgumentParser(description="Demo for RingLed display_ping")
    parser.add_argument("--flipped", action="store_true", help="Flip ring orientation")
    parser.add_argument("--interval", type=float, default=0.08, help="Frame interval in seconds")
    parser.add_argument("--size-a", type=float, default=1.4, help="Ping A blob size in pixels")
    parser.add_argument("--size-b", type=float, default=1.4, help="Ping B blob size in pixels")
    args = parser.parse_args()

    if args.size_a <= 0 or args.size_b <= 0:
        raise ValueError("--size-a and --size-b must be > 0")

    ring = RingLed(board.MOSI, flipped=args.flipped, pixel_count=24, brightness=0.2)

    print("Running ping demo:")
    print("Ping A starts at 330 deg, distance 5; moves 10 deg down every second")
    print("Ping B stays at 90 deg, moves distance 10 -> 0 -> 10 by 1 every 0.5s")
    print(f"Ping sizes: A={args.size_a}, B={args.size_b}")
    print("Press Ctrl+C to stop")

    ping_a_angle = 330.0
    ping_a_distance = 5.0

    ping_b_angle = 90.0
    ping_b_distance = 10.0
    ping_b_step = -1.0

    next_angle_update = time.monotonic() + 1.0
    next_distance_update = time.monotonic() + 0.5

    try:
        while True:
            now = time.monotonic()

            while now >= next_angle_update:
                ping_a_angle = (ping_a_angle - 10.0) % 360.0
                next_angle_update += 1.0

            while now >= next_distance_update:
                ping_b_distance += ping_b_step
                if ping_b_distance <= 0.0:
                    ping_b_distance = 0.0
                    ping_b_step = 1.0
                elif ping_b_distance >= 10.0:
                    ping_b_distance = 10.0
                    ping_b_step = -1.0
                next_distance_update += 0.5

            ring.display_ping([
                [ping_a_angle, ping_a_distance, args.size_a],
                [ping_b_angle, ping_b_distance, args.size_b],
            ])
            print(
                f"PingA angle={ping_a_angle:6.1f} distance={ping_a_distance:4.1f} size={args.size_a:3.1f} | "
                f"PingB angle={ping_b_angle:6.1f} distance={ping_b_distance:4.1f} size={args.size_b:3.1f}",
                flush=True,
            )

            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        ring.clear()


if __name__ == "__main__":
    main()
