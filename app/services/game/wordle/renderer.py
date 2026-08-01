from __future__ import annotations

import functools

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from app.core.enums.letterstate import LetterState
from app.core.constants.game.wordle import WORD_LENGTH, MAX_ATTEMPTS
from app.core.constants.system.paths import FONT_PATH

from app.types.services_result.game import GuessResult
from app.utils.logger import system_logger

BACKGROUND = (18, 18, 19)

EMPTY_FILL = (18, 18, 19)
EMPTY_BORDER = (58, 58, 60)

CORRECT_COLOR = (83, 141, 78)
PRESENT_COLOR = (181, 159, 59)
ABSENT_COLOR = (58, 58, 60)

TEXT_COLOR = (255, 255, 255)


STATE_COLORS = {
    LetterState.CORRECT: CORRECT_COLOR,
    LetterState.PRESENT: PRESENT_COLOR,
    LetterState.ABSENT: ABSENT_COLOR,
}


@functools.lru_cache(maxsize=1)
def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Загружает шрифт для букв"""

    if not FONT_PATH.exists():
        system_logger.warning(f"Font not found at: {FONT_PATH}")
        system_logger.warning("Using default font. Check your project structure and Dockerfile.")
        return ImageFont.load_default()

    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except OSError as e:
        system_logger.error(f"Error loading font: {e}")
        return ImageFont.load_default()


def render_board(guesses: list[GuessResult], cell_size: int = 48, gap: int = 5) -> bytes:
    """Нарисовать сетку 6x5 и вернуть PNG-байты"""

    padding = 16
    radius = 4
    font = load_font(int(cell_size * 0.55))

    width = (WORD_LENGTH * cell_size + (WORD_LENGTH - 1) * gap + padding * 2)
    height = (MAX_ATTEMPTS * cell_size + (MAX_ATTEMPTS - 1) * gap + padding * 2)

    image = Image.new("RGB", (width, height), BACKGROUND)

    draw = ImageDraw.Draw(image)

    for row in range(MAX_ATTEMPTS):
        guess = guesses[row] if row < len(guesses) else None

        for col in range(WORD_LENGTH):
            x = padding + col * (cell_size + gap)
            y = padding + row * (cell_size + gap)

            x2 = x + cell_size
            y2 = y + cell_size

            if guess is None:
                draw.rounded_rectangle(
                    (x, y, x2, y2),
                    radius=radius,
                    fill=EMPTY_FILL,
                    outline=EMPTY_BORDER,
                    width=2,
                )
                continue

            state = guess.states[col]
            color = STATE_COLORS[state]

            draw.rounded_rectangle(
                (x, y, x2, y2),
                radius=radius,
                fill=color,
            )

            letter = guess.word[col]

            bbox = draw.textbbox(
                (0, 0),
                letter,
                font=font,
            )

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            draw.text(
            (
                    x + (cell_size - text_width) // 2,
                    y + (cell_size - text_height) // 2 - 3,
                ),
                letter,
                font=font,
                fill=TEXT_COLOR,
            )

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)

    return buffer.getvalue()