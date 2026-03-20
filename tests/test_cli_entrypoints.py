from __future__ import annotations

import main as root_main

from langswitcher import __main__ as package_main
from langswitcher.cli import main as cli_main


def test_script_entrypoint_delegates_to_cli() -> None:
    assert root_main.main is cli_main


def test_package_entrypoint_delegates_to_cli() -> None:
    assert package_main.main is cli_main
