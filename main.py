"""CLI entrypoint for LangSwitcher."""

from __future__ import annotations

import argparse
import os
import sys

import keyboard
from loguru import logger

from langswitcher.app import LanguageSwitcherApp
from langswitcher.config import ConfigError, load_app_config, resolve_config_path
from langswitcher.hotkeys import KeyboardListener
from langswitcher.layout_service import WindowsLayoutService
from langswitcher.logging_setup import configure_logging
from langswitcher.version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Switch layout by left/right Shift")
    parser.add_argument("--config", help="Path to YAML config file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    configure_logging("INFO")

    if os.name != "nt":
        if _is_wsl():
            logger.error(
                "WSL detected: global keyboard hooks and Windows layout API are not available "
                "from Linux Python process. Run this app with Windows Python instead."
            )
        else:
            logger.error("This app targets Windows 10. Current OS is unsupported.")
        return 3

    config_path = resolve_config_path(args.config)
    logger.info("Reading config file: {}", config_path)
    try:
        config = load_app_config(config_path)
    except ConfigError as exc:
        logger.error("Configuration error: {}", exc)
        return 2
    configure_logging(config.log_level)
    logger.info("Application log level set to {}", config.log_level)
    logger.info("Hotkey mapping loaded: {}", config.hotkeys)

    listener = KeyboardListener(keyboard)
    layout_service = WindowsLayoutService()
    app = LanguageSwitcherApp(config=config, listener=listener, layout_service=layout_service)
    logger.info("LangSwitcher v{} is starting", __version__)

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        app.stop()
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Runtime error: {}", exc)
        app.stop()
        return 1
    logger.info("Application stopped")
    return 0


def _is_wsl() -> bool:
    # Русский комментарий: в WSL os.name == 'posix', поэтому отличаем его
    # по системной информации Linux-ядра.
    if os.name == "nt":
        return False
    try:
        return "microsoft" in os.uname().release.lower()
    except AttributeError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
