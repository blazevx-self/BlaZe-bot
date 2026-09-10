import random
import numpy as np
import imageio.v2 as imageio

from io import BytesIO
from PIL import Image, ImageDraw

from app.core.enums.lottery import LotteryColor
from app.core.constants.game.lottery import LOTTERY_COLORS

from app.utils.logger import lottery_logger

class LotteryVideoGenerator:
    """Генерирует анимацию лотереи и возвращает её в виде байтов."""

    def __init__(
        self,
        video_size: tuple[int, int] = (480, 480),
        fps: int = 30,
        spin_duration: float = 5.0,
        pause_duration: float = 3.0,
        circle_radius: int = 50,
        circle_spacing: int = 140,
        deceleration_start: float = 0.5,
    ) -> None:
        self.video_w, self.video_h = video_size
        self.fps = fps
        self.spin_duration = spin_duration
        self.pause_duration = pause_duration
        self.circle_radius = circle_radius
        self.circle_spacing = circle_spacing
        self.deceleration_start = deceleration_start

        self.frame_ms = round(1000 / fps)
        self.spin_frames = max(round(spin_duration * fps), 1)
        self.pause_frames = max(round(pause_duration * fps), 1)

        self.strip_y = self.video_h // 2

        self.arrow_color = (255, 255, 255)
        self.arrow_size = 30

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        return 1 - (1 - t) ** 3

    def _compute_scroll(self, frame: int, total_scroll: float,) -> float:
        norm = min(frame / self.spin_frames, 1.0)

        scroll_phase1 = total_scroll * 0.43
        scroll_phase2 = total_scroll - scroll_phase1

        if norm <= self.deceleration_start:
            return scroll_phase1 * (norm / self.deceleration_start)

        local = (norm - self.deceleration_start) / (1 - self.deceleration_start)

        return scroll_phase1 + scroll_phase2 * self._ease_out_cubic(local)

    @staticmethod
    def _random_color() -> LotteryColor:
        return random.choice(list(LOTTERY_COLORS))

    @staticmethod
    def _get_color(color: LotteryColor) -> tuple[int, int, int]:
        try:
            return LOTTERY_COLORS[color]
        except KeyError:
            raise ValueError(f"Неизвестный цвет лотереи: {color!r}")

    def _draw_circle(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        color: tuple[int, int, int]
    ) -> None:
        radius = self.circle_radius

        draw.ellipse(
            [
                cx - radius + 4,
                cy - radius + 4,
                cx + radius + 4,
                cy + radius + 4
            ],
            fill=(20, 20, 20)
        )

        draw.ellipse(
            [
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius
            ],
            fill=color
        )

        highlight_radius = max(radius // 4, 5)

        highlight_x = cx - radius // 3
        highlight_y = cy - radius // 3

        r, g, b = color
        lighter: tuple[int, int, int] = (min(255, r + 80), min(255, g + 80), min(255, b + 80))

        draw.ellipse(
            [
                    highlight_x - highlight_radius,
                    highlight_y - highlight_radius // 2,
                    highlight_x + highlight_radius,
                    highlight_y + highlight_radius // 2
            ],
            fill=lighter
        )

    def _draw_arrow(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int,
        y_tip: int
    ) -> None:
        stem_top = y_tip + self.arrow_size
        stem_bottom = y_tip + self.arrow_size * 2 + 10

        draw.line(
         [
                (cx, stem_top),
                (cx, stem_bottom),
            ],
            fill=self.arrow_color,
            width=4
        )

        draw.line(
            [
                (cx, y_tip),
                (cx - self.arrow_size, stem_top)
            ],
            fill=self.arrow_color,
            width=4
        )

        draw.line(
            [
                (cx, y_tip),
                (cx + self.arrow_size, stem_top)
            ],
            fill=self.arrow_color,
            width=4,
        )

    def _make_frame(
        self,
        scroll: float,
        winner_color: LotteryColor,
        winner_position: int,
        seed: int
    ) -> np.ndarray:
        image = Image.new(
            "RGB",
            (self.video_w, self.video_h),
            (10, 10, 10)
        )

        draw = ImageDraw.Draw(image)

        center_x = self.video_w // 2
        padding = self.circle_radius + 30

        slot_left = (int((scroll - center_x - padding) / self.circle_spacing) - 1)
        slot_right = (int((scroll + center_x + padding) / self.circle_spacing) + 1)

        for position in range(slot_left, slot_right + 1):
            cx = int(center_x + position * self.circle_spacing - scroll)

            if cx < -padding or cx > self.video_w + padding:
                continue

            if position == winner_position:
                color = winner_color
            else:
                rng = random.Random(seed ^ (position * 2654435761 & 0xFFFFFFFF))
                color = rng.choice(list(LOTTERY_COLORS))

            color_rgb = self._get_color(color)

            distance = abs(cx - center_x)
            max_distance = (self.video_w // 2 + self.circle_radius)

            alpha = max(0.3, 1.0 - distance / max_distance * 0.7)

            r, g, b = color_rgb
            faded_color: tuple[int, int, int] = (int(r * alpha), int(g * alpha), int(b * alpha))

            self._draw_circle(draw, cx, self.strip_y, faded_color)

        winner_half = self.circle_radius + 15
        line_color = (180, 180, 180)

        draw.line(
            [
                (center_x - winner_half, self.strip_y - self.circle_radius - 20),
                (center_x - winner_half, self.strip_y + self.circle_radius + 20)
            ],
            fill=line_color,
            width=2
        )

        draw.line(
            [
                (center_x + winner_half, self.strip_y - self.circle_radius - 20),
                (center_x + winner_half, self.strip_y + self.circle_radius + 20)
            ],
            fill=line_color,
            width=2
        )

        self._draw_arrow(draw, center_x, self.strip_y + self.circle_radius + 25,)

        return np.array(image)

    def generate(self, winner_color: LotteryColor) -> bytes:
        """Генерирует GIF с указанным выигрышным цветом."""
        if winner_color not in LOTTERY_COLORS:
            raise ValueError(
                f"Неизвестный цвет лотереи: {winner_color!r}"
            )

        seed = random.randint(0, 2 ** 31,)
        start_scroll = (random.randint(50, 200) * self.circle_spacing)
        extra_slots = random.randint(15, 30)

        winner_position = (round(start_scroll / self.circle_spacing) + extra_slots)

        final_scroll = (winner_position * self.circle_spacing)
        total_scroll = (final_scroll - start_scroll)

        lottery_logger.debug(
            "Lottery animation started | winner=%s | "
            "winner_position=%d | total_scroll=%.1f",
            winner_color.value, winner_position, total_scroll
        )

        frames: list[np.ndarray] = []

        for frame in range(self.spin_frames):
            scroll = (start_scroll + self._compute_scroll(frame, total_scroll))

            frame_data = self._make_frame(
                scroll=scroll,
                winner_color=winner_color,
                winner_position=winner_position,
                seed=seed,
            )

            frames.append(frame_data)

        final_frame = self._make_frame(
            scroll=final_scroll,
            winner_color=winner_color,
            winner_position=winner_position,
            seed=seed,
        )

        frames.extend([final_frame] * self.pause_frames)

        buffer = BytesIO()

        # noinspection PyTypeChecker
        writer = imageio.get_writer(
            buffer,
            format="mp4",
            fps=self.fps,
            codec="libx264",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "23"],
        )

        for frame_data in frames:
            writer.append_data(frame_data)

        writer.close()

        data = buffer.getvalue()

        lottery_logger.info(
            "Lottery animation generated | winner=%s | "
            "frames=%d | size=%.1f KB",
            winner_color.value, len(frames), len(data) / 1024,
        )

        return data