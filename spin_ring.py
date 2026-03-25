import board
from ring_led import RingLed


PIN = board.MOSI
FLIPPED = False
BLUE = (0, 0, 255)
SPIN_SPEED = 20


def main():
    try:
        ring = RingLed(PIN, flipped=FLIPPED, pixel_count=24, brightness=0.2)
    except (OSError, RuntimeError) as error:
        error_text = str(error).lower()
        if "spidev" in error_text or "does not exist" in error_text or "permission denied" in error_text:
            print("SPI NeoPixel backend could not access /dev/spidev.")
            print("Enable SPI: sudo raspi-config -> Interface Options -> SPI -> Enable")
            print("Then ensure your user is in the 'spi' group and relogin.")
            print("Data pin for this script is GPIO10 (MOSI), physical pin 19.")
            return
        raise

    ring.spin_ring(BLUE, SPIN_SPEED)


if __name__ == "__main__":
    main()