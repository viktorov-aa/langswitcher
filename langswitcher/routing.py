"""Routing keyboard events to target layouts."""

from __future__ import annotations

from dataclasses import dataclass

from .config import normalize_key_name


@dataclass
class ShiftKeyRouter:
    """Maps normalized key names to language layout codes."""

    hotkey_map: dict[str, str]

    def route_event(self, key_name: str) -> str | None:
        normalized = normalize_key_name(key_name)
        return self.hotkey_map.get(normalized)
