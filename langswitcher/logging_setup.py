"""Unified program output via loguru. Colors are Solarized Dark, without bold INFO."""

from __future__ import annotations

import sys

from loguru import logger

# Ethan Schoonover, Solarized: https://ethanschoonover.com/solarized/
# Layout like loguru's default: green time, colored levels, no <bold>.
_YELLOW = "#b58900"
_ORANGE = "#cb4b16"
_RED = "#dc322f"
_BLUE = "#268bd2"
_CYAN = "#2aa198"
_GREEN = "#859900"

_configured = False


def _reconfigure_stdio_utf8() -> None:
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    _reconfigure_stdio_utf8()
    logger.remove()
    logger.level("DEBUG", color=f"<fg {_CYAN}>")
    logger.level("INFO", color=f"<fg {_BLUE}>")
    logger.level("SUCCESS", color=f"<fg {_GREEN}>")
    logger.level("WARNING", color=f"<fg {_YELLOW}>")
    logger.level("ERROR", color=f"<fg {_RED}>")
    logger.level("CRITICAL", color=f"<fg {_ORANGE}>")
    logger.add(
        sys.stderr,
        format=(
            f"<fg {_GREEN}>{{time:YYYY-MM-DD HH:mm:ss}}</> | "
            "<level>{level:<7}</level> | "
            "<level>{message}</level>"
        ),
        level="INFO",
        colorize=True,
    )
    _configured = True
