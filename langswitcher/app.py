"""Application orchestration."""

from __future__ import annotations

from loguru import logger

from .config import AppConfig
from .layout_service import LayoutService
from .routing import ShiftKeyRouter


class LanguageSwitcherApp:
    """Coordinates routing and layout switching."""

    def __init__(self, config: AppConfig, listener: object, layout_service: LayoutService) -> None:
        self._router = ShiftKeyRouter(config.hotkeys)
        self._listener = listener
        self._layout_service = layout_service
        self._config = config

    def run(self) -> None:
        logger.info("Starting keyboard listener")
        self._listener.start(self._on_key)
        logger.info("Listener started; waiting for key events")
        self._listener.wait_forever()

    def stop(self) -> None:
        logger.info("Stopping keyboard listener")
        self._listener.stop()

    def _on_key(self, key_name: str) -> None:
        target_layout = self._router.route_event(key_name)
        if target_layout is None:
            logger.debug("Ignoring non-mapped key event: {}", key_name)
            return
        logger.debug("Mapped key '{}' to target layout '{}'", key_name, target_layout)
        changed = self._layout_service.apply_layout(target_layout)
        if changed:
            logger.debug("Layout switched to '{}'", target_layout)
        else:
            logger.debug("Layout '{}' was already active", target_layout)
