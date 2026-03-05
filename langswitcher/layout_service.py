"""Services for applying keyboard layouts."""

from __future__ import annotations

import ctypes
import os
from abc import ABC, abstractmethod


class LayoutService(ABC):
    """Interface for layout switch service."""

    @abstractmethod
    def apply_layout(self, layout: str) -> bool:
        """Apply target layout. Returns True if layout changed."""


class WindowsLayoutService(LayoutService):
    """Windows API-backed layout switching service."""

    LAYOUT_IDS = {"en": "00000409", "ru": "00000419"}

    def __init__(self) -> None:
        self._last_applied: str | None = None
        self._user32 = getattr(ctypes, "windll", None)
        if self._user32 is not None:
            self._user32 = self._user32.user32

    def apply_layout(self, layout: str) -> bool:
        layout = layout.strip().lower()
        if layout not in self.LAYOUT_IDS:
            raise ValueError(f"Unsupported layout '{layout}'")

        if self._last_applied == layout:
            return False

        if os.name != "nt" or self._user32 is None:
            raise RuntimeError("Windows layout switching is available only on Windows")

        # Русский комментарий: в Windows раскладки активируются через HKL-идентификатор.
        # Сначала загружаем раскладку, затем явно активируем ее для текущего контекста.
        hkl = self._user32.LoadKeyboardLayoutW(self.LAYOUT_IDS[layout], 1)
        if not hkl:
            raise RuntimeError(f"Failed to load layout '{layout}'")
        result = self._user32.ActivateKeyboardLayout(hkl, 0)
        if not result:
            raise RuntimeError(f"Failed to activate layout '{layout}'")

        self._last_applied = layout
        return True
