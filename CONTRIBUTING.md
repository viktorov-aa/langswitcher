# Contributing

LangSwitcher is intentionally small, so contributions work best when they stay focused and easy to review.

## Development flow

1. Create and activate a virtual environment.
2. Install development dependencies with `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`.
3. Run `.\.venv\Scripts\python.exe -m pytest -q` before opening a pull request.

## Scope

- Prefer small fixes and narrowly scoped improvements.
- Keep Windows-specific behavior explicit in both code and documentation.
- Update the README when user-facing behavior or setup steps change.
- Preserve the existing OpenSpec workflow for substantial changes.

## Code style

- Use clear, concise English for comments and user-facing text.
- Avoid broad refactors unless they directly support the change you are making.
- Add or update tests when behavior changes.
