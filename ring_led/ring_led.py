import time

import board
import busio
import neopixel
import neopixel_spi


class RingLed:
    PIXEL_COUNT = 24
    BLOB_RADIUS_PIXELS = 1.4
    FLASH_DURATION = 0.2
    SPIN_TAIL_PIXELS = 4

    def __init__(self, pin, flipped=False, pixel_count=24, brightness=0.2, blob_radius_pixels=None):
        self.pin = pin
        self.flipped = flipped
        self.pixel_count = pixel_count
        self.blob_radius_pixels = blob_radius_pixels if blob_radius_pixels is not None else self.BLOB_RADIUS_PIXELS

        mosi_pin = getattr(board, "MOSI", None)
        if mosi_pin is not None and pin == mosi_pin:
            sck_pin = getattr(board, "SCK", None) or getattr(board, "SCLK", None)
            if sck_pin is None:
                raise RuntimeError("Could not resolve SPI clock pin (SCK/SCLK)")
            spi = busio.SPI(clock=sck_pin, MOSI=mosi_pin)
            self._pixels = neopixel_spi.NeoPixel_SPI(
                spi,
                pixel_count,
                brightness=brightness,
                auto_write=False,
                pixel_order=neopixel_spi.GRB,
            )
            self.backend = "spi"
        else:
            self._pixels = neopixel.NeoPixel(
                pin,
                pixel_count,
                brightness=brightness,
                auto_write=False,
                pixel_order=neopixel.GRB,
            )
            self.backend = "gpio"

    def _clamp(self, value, low, high):
        return max(low, min(high, value))

    def _render_with_delegate(self, color_delegate):
        for index in range(self.pixel_count):
            self._pixels[index] = color_delegate(index)
        self._pixels.show()

    def _normalize_angle(self, angle):
        return angle % 360.0

    def _pixel_angle(self, index):
        return (index * 360.0) / self.pixel_count

    def _logical_to_physical_angle(self, angle):
        angle = self._normalize_angle(angle)
        if self.flipped:
            return (180.0 - angle) % 360.0
        return angle

    def _physical_to_logical_angle(self, angle):
        angle = self._normalize_angle(angle)
        if self.flipped:
            return (180.0 - angle) % 360.0
        return angle

    def _angle_to_pixel_float(self, angle):
        angle = self._logical_to_physical_angle(angle)
        return (angle / 360.0) * self.pixel_count

    def _distance_to_color(self, distance):
        t = self._clamp(distance / 10.0, 0.0, 1.0)
        return (int(255 * (1.0 - t)), int(255 * t), 0)

    def clear(self):
        self._pixels.fill((0, 0, 0))
        self._pixels.show()

    def close(self):
        self.clear()

    def flash_quadrant(self, side, color):
        if side not in (1, 2, 3, 4):
            raise ValueError("side must be 1 (top), 2 (right), 3 (bottom), or 4 (left)")

        def in_side(logical_angle):
            if side == 1:
                return logical_angle >= 315 or logical_angle < 45
            if side == 2:
                return 45 <= logical_angle < 135
            if side == 3:
                return 135 <= logical_angle < 225
            return 225 <= logical_angle < 315

        def quadrant_delegate(index):
            logical_angle = self._physical_to_logical_angle(self._pixel_angle(index))
            return color if in_side(logical_angle) else (0, 0, 0)

        self._render_with_delegate(quadrant_delegate)
        time.sleep(self.FLASH_DURATION)
        self.clear()

    def display_ping(self, polar_coordinate_array):
        best_strength = [0.0 for _ in range(self.pixel_count)]
        best_color = [[0.0, 0.0, 0.0] for _ in range(self.pixel_count)]

        for coordinate in polar_coordinate_array:
            if len(coordinate) not in (2, 3):
                raise ValueError("Each polar coordinate must be [angle, distance] or [angle, distance, size]")

            angle, distance = coordinate[0], coordinate[1]
            blob_radius = float(coordinate[2]) if len(coordinate) == 3 else float(self.blob_radius_pixels)
            if blob_radius <= 0:
                raise ValueError("Ping size must be > 0")
            base_color = self._distance_to_color(float(distance))

            center_pixel = self._angle_to_pixel_float(float(angle))

            for index in range(self.pixel_count):
                pixel_distance = abs(index - center_pixel)
                pixel_distance = min(pixel_distance, self.pixel_count - pixel_distance)
                if pixel_distance > blob_radius:
                    continue

                linear = 1.0 - (pixel_distance / blob_radius)
                weight = linear * linear
                if weight <= best_strength[index]:
                    continue

                best_strength[index] = weight
                best_color[index][0] = base_color[0] * weight
                best_color[index][1] = base_color[1] * weight
                best_color[index][2] = base_color[2] * weight

        def ping_delegate(index):
            return (
                int(self._clamp(best_color[index][0], 0, 255)),
                int(self._clamp(best_color[index][1], 0, 255)),
                int(self._clamp(best_color[index][2], 0, 255)),
            )

        self._render_with_delegate(ping_delegate)

    def spin_ring(self, color, speed):
        if speed <= 0:
            raise ValueError("speed must be > 0")

        delay = 1.0 / float(speed)

        try:
            while True:
                for head in range(self.pixel_count):

                    def spin_delegate(index):
                        behind = (head - index) % self.pixel_count
                        if behind >= self.SPIN_TAIL_PIXELS:
                            return (0, 0, 0)
                        intensity = (self.SPIN_TAIL_PIXELS - behind) / self.SPIN_TAIL_PIXELS
                        return (
                            int(color[0] * intensity),
                            int(color[1] * intensity),
                            int(color[2] * intensity),
                        )

                    self._render_with_delegate(spin_delegate)
                    time.sleep(delay)
        except KeyboardInterrupt:
            self.clear()
