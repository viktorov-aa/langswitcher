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
    LANG_IDS = {name: int(layout_id[-4:], 16) for name, layout_id in LAYOUT_IDS.items()}
    WM_INPUTLANGCHANGEREQUEST = 0x0050
    KLF_ACTIVATE = 0x00000001

    def __init__(self) -> None:
        self._last_applied: str | None = None
        self._user32 = getattr(ctypes, "windll", None)
        if self._user32 is not None:
            self._user32 = self._user32.user32

    def apply_layout(self, layout: str) -> bool:
        layout = layout.strip().lower()
        if layout not in self.LAYOUT_IDS:
            raise ValueError(f"Unsupported layout '{layout}'")

        if os.name != "nt" or self._user32 is None:
            raise RuntimeError("Windows layout switching is available only on Windows")

        active_layout = self._get_active_layout()
        if active_layout is not None:
            self._last_applied = active_layout
            if active_layout == layout:
                return False

        # Русский комментарий: в Windows раскладки активируются через HKL-идентификатор.
        # Сначала загружаем раскладку, затем отправляем запрос смены в foreground-окно.
        hkl = self._user32.LoadKeyboardLayoutW(self.LAYOUT_IDS[layout], self.KLF_ACTIVATE)
        if not hkl:
            raise RuntimeError(f"Failed to load layout '{layout}'")

        foreground = self._user32.GetForegroundWindow()
        if foreground:
            posted = self._user32.PostMessageW(
                foreground,
                self.WM_INPUTLANGCHANGEREQUEST,
                0,
                hkl,
            )
            if not posted:
                raise RuntimeError(f"Failed to request layout change '{layout}'")
        else:
            # fallback для редких случаев без foreground-окна (например, ранний старт).
            result = self._user32.ActivateKeyboardLayout(hkl, 0)
            if not result:
                raise RuntimeError(f"Failed to activate layout '{layout}'")

        self._last_applied = layout
        return True

    def _get_active_layout(self) -> str | None:
        foreground = self._user32.GetForegroundWindow()
        thread_id = 0
        if foreground:
            thread_id = self._user32.GetWindowThreadProcessId(foreground, None)

        hkl = self._user32.GetKeyboardLayout(thread_id)
        if not hkl:
            return None

        lang_id = int(hkl) & 0xFFFF
        for layout, expected_lang_id in self.LANG_IDS.items():
            if expected_lang_id == lang_id:
                return layout

        return None
