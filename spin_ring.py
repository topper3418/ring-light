import time

import board
import busio
import neopixel_spi


PIXEL_COUNT = 24
BRIGHTNESS = 0.2
STEP_DELAY = 0.05
TAIL_LENGTH = 4
BLUE = (0, 0, 255)


def scale_color(color, factor):
    return tuple(int(channel * factor) for channel in color)


def main():
    sck_pin = getattr(board, "SCK", None) or getattr(board, "SCLK", None)
    mosi_pin = getattr(board, "MOSI", None)

    if sck_pin is None or mosi_pin is None:
        print("Could not find SPI pins on this board definition.")
        print("Expected SCK/SCLK and MOSI for Raspberry Pi SPI0.")
        return

    try:
        spi = busio.SPI(clock=sck_pin, MOSI=mosi_pin)
        pixels = neopixel_spi.NeoPixel_SPI(
            spi,
            PIXEL_COUNT,
            brightness=BRIGHTNESS,
            auto_write=False,
            pixel_order=neopixel_spi.GRB,
        )
    except (OSError, RuntimeError) as error:
        error_text = str(error).lower()
        if "spidev" in error_text or "does not exist" in error_text or "permission denied" in error_text:
            print("SPI NeoPixel backend could not access /dev/spidev.")
            print("Enable SPI: sudo raspi-config -> Interface Options -> SPI -> Enable")
            print("Then ensure your user is in the 'spi' group and relogin.")
            print("Data pin for this script is GPIO10 (MOSI), physical pin 19.")
            return
        raise

    try:
        while True:
            for head in range(PIXEL_COUNT):
                pixels.fill((0, 0, 0))

                for offset in range(TAIL_LENGTH):
                    index = (head - offset) % PIXEL_COUNT
                    intensity = (TAIL_LENGTH - offset) / TAIL_LENGTH
                    pixels[index] = scale_color(BLUE, intensity)

                pixels.show()
                time.sleep(STEP_DELAY)
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()


if __name__ == "__main__":
    main()