"""Keyboard hook integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from loguru import logger

from .config import normalize_key_name


class KeyboardListener:
    """Global keyboard listener based on the `keyboard` package."""

    def __init__(self, keyboard_module: Any) -> None:
        self._keyboard = keyboard_module
        self._hook = None
        self._pending_shift_tap: str | None = None

    def start(self, on_key: Callable[[str], None]) -> None:
        # Русский комментарий: библиотека keyboard отдает множество событий.
        # Мы нормализуем имя и пропускаем дальше только нужные клавиши.
        def _handle(event: Any) -> None:
            event_type = getattr(event, "event_type", None)
            name = getattr(event, "name", None)
            scan_code = getattr(event, "scan_code", None)
            if not isinstance(event_type, str) or event_type not in {"down", "up"}:
                return
            if not isinstance(name, str):
                return
            normalized = normalize_key_name(name)
            normalized = self._normalize_shift_alias(normalized)
            normalized = self._normalize_shift(normalized, scan_code)
            is_shift = normalized in {"left_shift", "right_shift"}

            if event_type == "down":
                if is_shift:
                    if self._pending_shift_tap is None:
                        self._pending_shift_tap = normalized
                    elif self._pending_shift_tap != normalized:
                        self._pending_shift_tap = None
                else:
                    self._pending_shift_tap = None
                return

            if not is_shift:
                return
            if self._pending_shift_tap != normalized:
                return

            self._pending_shift_tap = None
            logger.debug("Keyboard tap event received: {} -> {}", name, normalized)
            on_key(normalized)

        self._hook = self._keyboard.hook(_handle)

    def wait_forever(self) -> None:
        # Русский комментарий: wait("esc") удерживает процесс активным,
        # при этом глобальный hook продолжает получать события Shift.
        self._keyboard.wait("esc")

    def stop(self) -> None:
        if self._hook is not None:
            self._keyboard.unhook(self._hook)
            self._hook = None

    @staticmethod
    def _normalize_shift(normalized_name: str, scan_code: Any) -> str:
        if normalized_name == "shift":
            if scan_code == 42:
                return "left_shift"
            if scan_code == 54:
                return "right_shift"
        return normalized_name

    @staticmethod
    def _normalize_shift_alias(normalized_name: str) -> str:
        if normalized_name in {"left_shift", "lshift", "shift_left"}:
            return "left_shift"
        if normalized_name in {"right_shift", "rshift", "shift_right"}:
            return "right_shift"
        return normalized_name
