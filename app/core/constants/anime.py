from pathlib import Path

ANIME_DIR = Path(__file__).resolve().parents[2] / "assets" / "anime"

MAX_VIDEO_SECONDS = 60
MAX_GIF_SECONDS = 15
CUT_TIMEOUT = 120

SCALE = "scale=-2:'min(720,ih)'"

VIDEO_ARGS = [
    "-map", "0:v:0", "-map", "0:a:0?",
    "-vf", SCALE,
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-tune", "animation",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart",
    "-threads", "2",
]

GIF_ARGS = [
    "-an",
    "-vf", SCALE,
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-tune", "animation",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    "-threads", "2",
]