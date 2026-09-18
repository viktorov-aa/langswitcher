from __future__ import annotations

import re
import sys

from loguru import logger

from langswitcher import logging_setup


def _reset_logging_setup() -> None:
    logging_setup._configured = False
    logger.remove()


def test_setup_logging_is_idempotent() -> None:
    _reset_logging_setup()
    logging_setup.setup_logging()
    handler_ids = set(logger._core.handlers)
    logging_setup.setup_logging()
    assert set(logger._core.handlers) == handler_ids


def test_setup_logging_uses_info_format(capsys) -> None:
    _reset_logging_setup()
    logging_setup.setup_logging()
    logger.debug("hidden debug")
    logger.info("hello")
    err = re.sub(r"\x1b\[[0-9;]*m", "", capsys.readouterr().err)
    assert "hidden debug" not in err
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INFO    \| hello", err)


def test_setup_logging_reconfigures_utf8_on_windows(monkeypatch) -> None:
    encodings: list[str] = []

    def fake_reconfigure(*, encoding: str, **_kwargs: object) -> None:
        encodings.append(encoding)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys.stdout, "reconfigure", fake_reconfigure, raising=False)
    monkeypatch.setattr(sys.stderr, "reconfigure", fake_reconfigure, raising=False)
    _reset_logging_setup()
    logging_setup.setup_logging()
    assert encodings == ["utf-8", "utf-8"]
