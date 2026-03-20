# LangSwitcher

LangSwitcher is a small Windows utility that switches the active keyboard layout with individual Shift taps:

- `Left Shift` -> English (`en`)
- `Right Shift` -> Russian (`ru`)

Current version: `0.0.2`

## Why this exists

If you regularly switch between English and Russian on Windows, the default OS shortcut can feel slower and less predictable than a dedicated key per layout. LangSwitcher keeps the interaction simple: tap the left or right Shift key on its own and the app forces the target layout.

## Platform support

- Supported: Windows 10 and Windows 11
- Not supported: WSL/Linux Python, macOS
- Requirement: global keyboard hooks must be allowed in the current Windows session

If you work from WSL, start the app with a Windows Python interpreter from PowerShell or Command Prompt instead of running it inside Linux.

## Quick start

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

You can also run the package entrypoint:

```bash
.\.venv\Scripts\python.exe -m langswitcher
```

Stop the app with `Ctrl+C` in the active terminal.

## Configuration

By default the app loads [`config/default_config.yaml`](config/default_config.yaml):

```yaml
log_level: INFO
hotkeys:
  left_shift: en
  right_shift: ru
```

Pass a custom config file if needed:

```bash
.\.venv\Scripts\python.exe main.py --config C:\path\to\config.yaml
```

Supported `log_level` values:

- `TRACE`
- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

Supported hotkey names:

- `left_shift`
- `right_shift`

Supported layouts:

- `en`
- `ru`

## Development

Install development dependencies:

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Run the test suite:

```bash
.\.venv\Scripts\python.exe -m pytest -q
```

## Logging

- Logging is handled by `loguru`
- Startup logs include the config path, effective log level, and loaded hotkey mapping
- With `log_level: DEBUG`, the app also logs Shift tap processing and layout-switch attempts

## Project layout

```text
langswitcher/
├── config/              Default YAML configuration
├── langswitcher/        Application package
├── scripts/             Helper scripts
├── tests/               Unit tests
├── main.py              Script entrypoint
└── openspec/            OpenSpec artifacts
```

## Dependencies

- `keyboard` for global keyboard hooks on Windows
- `loguru` for terminal logging
- `yamldataclassconfig` and `pyyaml` for YAML-backed configuration loading
- `pytest` for automated tests

## Versioning

This project follows Semantic Versioning:

- `MAJOR` for incompatible behavior changes
- `MINOR` for backward-compatible features
- `PATCH` for backward-compatible fixes

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
