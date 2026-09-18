from __future__ import annotations

from langswitcher.app import LanguageSwitcherApp
from langswitcher.config import AppConfig
from loguru import logger


class _FakeListener:
    def start(self, on_key) -> None:
        self.on_key = on_key

    def wait_forever(self) -> None:
        return

    def stop(self) -> None:
        return


class _FakeLayoutService:
    def apply_layout(self, layout: str) -> bool:
        self.layout = layout
        return True


def test_processed_key_is_logged_at_debug_not_info() -> None:
    records: list[str] = []
    handler_id = logger.add(lambda message: records.append(message.record["level"].name), level="DEBUG")
    try:
        app = LanguageSwitcherApp(
            config=AppConfig(
                hotkeys={"left_shift": "en", "right_shift": "ru"},
                log_level="INFO",
            ),
            listener=_FakeListener(),
            layout_service=_FakeLayoutService(),
        )
        app._on_key("left_shift")
    finally:
        logger.remove(handler_id)

    assert "INFO" not in records
    assert "DEBUG" in records
