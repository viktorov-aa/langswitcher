import tempfile
from pathlib import Path

import pytest

from langswitcher.config import load_app_config
from langswitcher.errors import ConfigError


def _write_yaml(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


def test_load_valid_yaml_config() -> None:
    path = _write_yaml(
        "log_level: DEBUG\n"
        "hotkeys:\n"
        "  left_shift: en\n"
        "  right_shift: ru\n"
    )
    config = load_app_config(path)
    assert config.hotkeys["left_shift"] == "en"
    assert config.hotkeys["right_shift"] == "ru"
    assert config.log_level == "DEBUG"


def test_invalid_layout_raises_error() -> None:
    path = _write_yaml(
        "log_level: INFO\n"
        "hotkeys:\n"
        "  left_shift: de\n"
        "  right_shift: ru\n"
    )
    with pytest.raises(ConfigError):
        load_app_config(path)


def test_invalid_log_level_raises_error() -> None:
    path = _write_yaml(
        "log_level: VERBOSE\n"
        "hotkeys:\n"
        "  left_shift: en\n"
        "  right_shift: ru\n"
    )
    with pytest.raises(ConfigError):
        load_app_config(path)


def test_missing_log_level_uses_default_info() -> None:
    path = _write_yaml(
        "hotkeys:\n"
        "  left_shift: en\n"
        "  right_shift: ru\n"
    )
    config = load_app_config(path)
    assert config.log_level == "INFO"


def test_non_mapping_root_raises_error() -> None:
    path = _write_yaml("- item1\n- item2\n")
    with pytest.raises(ConfigError):
        load_app_config(path)


def test_malformed_yaml_raises_error() -> None:
    path = _write_yaml("hotkeys: [left_shift: en\n")
    with pytest.raises(ConfigError):
        load_app_config(path)
