"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from dataclasses_json import dataclass_json
from yamldataclassconfig.config import YamlDataClassConfig

from .errors import ConfigError

DEFAULT_MAPPING = {"left_shift": "en", "right_shift": "ru"}
ALLOWED_KEYS = frozenset(DEFAULT_MAPPING.keys())
ALLOWED_LAYOUTS = frozenset(DEFAULT_MAPPING.values())
ALLOWED_LOG_LEVELS = frozenset({"TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


@dataclass(frozen=True)
class AppConfig:
    """Validated application settings."""

    hotkeys: dict[str, str]
    log_level: str


@dataclass_json
@dataclass
class RawConfig(YamlDataClassConfig):
    """Raw YAML model loaded via yamldataclassconfig."""

    hotkeys: dict = field(default_factory=dict)
    log_level: str = "INFO"


def resolve_config_path(cli_path: str | None) -> Path:
    """Resolve config path from CLI argument or default location."""
    if cli_path:
        return Path(cli_path).expanduser().resolve()
    return (Path(__file__).resolve().parent.parent / "config" / "default_config.yaml").resolve()


def load_app_config(path: Path) -> AppConfig:
    """Load and validate YAML config from path."""
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        raw = _load_raw_config(path)
    except Exception as exc:  # noqa: BLE001
        raise ConfigError(f"Failed to parse config '{path}': {exc}") from exc

    hotkeys = _validate_hotkeys(raw.hotkeys)
    log_level = _validate_log_level(raw.log_level)
    return AppConfig(hotkeys=hotkeys, log_level=log_level)


def _validate_hotkeys(raw_hotkeys: object) -> dict[str, str]:
    if not isinstance(raw_hotkeys, dict):
        raise ConfigError("Config field 'hotkeys' must be a mapping")

    normalized: dict[str, str] = {}
    for raw_key, raw_layout in raw_hotkeys.items():
        if not isinstance(raw_key, str):
            raise ConfigError("All hotkey names must be strings")
        if not isinstance(raw_layout, str):
            raise ConfigError(f"Layout for key '{raw_key}' must be a string")

        key = normalize_key_name(raw_key)
        layout = raw_layout.strip().lower()
        if key not in ALLOWED_KEYS:
            raise ConfigError(
                f"Unsupported hotkey '{raw_key}'. Allowed keys: {sorted(ALLOWED_KEYS)}"
            )
        if layout not in ALLOWED_LAYOUTS:
            raise ConfigError(
                f"Unsupported layout '{raw_layout}'. Allowed layouts: {sorted(ALLOWED_LAYOUTS)}"
            )
        normalized[key] = layout

    missing = ALLOWED_KEYS.difference(normalized.keys())
    if missing:
        raise ConfigError(f"Missing required hotkeys: {sorted(missing)}")

    return normalized


def normalize_key_name(key_name: str) -> str:
    """Normalize hotkey text to internal representation."""
    return key_name.strip().lower().replace(" ", "_").replace("-", "_")


def _validate_log_level(raw_level: object) -> str:
    if not isinstance(raw_level, str):
        raise ConfigError("Config field 'log_level' must be a string")
    level = raw_level.strip().upper()
    if level not in ALLOWED_LOG_LEVELS:
        raise ConfigError(
            f"Unsupported log level '{raw_level}'. Allowed levels: {sorted(ALLOWED_LOG_LEVELS)}"
        )
    return level


def _load_raw_config(path: Path) -> RawConfig:
    # NOTE: keep unparameterized `dict` in RawConfig to avoid runtime issues in
    # yamldataclassconfig validation on Python 3.12 with generic aliases.
    config = RawConfig.create()
    config.load(path=path, path_is_absolute=True)
    return config
