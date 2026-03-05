from langswitcher.hotkeys import KeyboardListener


def test_normalize_shift_scan_code_left() -> None:
    assert KeyboardListener._normalize_shift("shift", 42) == "left_shift"


def test_normalize_shift_scan_code_right() -> None:
    assert KeyboardListener._normalize_shift("shift", 54) == "right_shift"


def test_normalize_shift_alias_left() -> None:
    assert KeyboardListener._normalize_shift_alias("lshift") == "left_shift"


def test_normalize_shift_alias_right() -> None:
    assert KeyboardListener._normalize_shift_alias("shift_right") == "right_shift"


class _FakeKeyboard:
    def __init__(self) -> None:
        self.handler = None

    def hook(self, handler):
        self.handler = handler
        return "hook-id"

    def unhook(self, _hook) -> None:
        return


class _Event:
    def __init__(self, event_type: str, name: str, scan_code: int | None = None) -> None:
        self.event_type = event_type
        self.name = name
        self.scan_code = scan_code


def test_shift_tap_emits_callback_on_keyup() -> None:
    keyboard = _FakeKeyboard()
    listener = KeyboardListener(keyboard)
    captured: list[str] = []
    listener.start(captured.append)

    keyboard.handler(_Event("down", "shift", 42))
    keyboard.handler(_Event("up", "shift", 42))

    assert captured == ["left_shift"]


def test_shift_combo_does_not_emit_callback() -> None:
    keyboard = _FakeKeyboard()
    listener = KeyboardListener(keyboard)
    captured: list[str] = []
    listener.start(captured.append)

    keyboard.handler(_Event("down", "shift", 42))
    keyboard.handler(_Event("down", "a", 30))
    keyboard.handler(_Event("up", "a", 30))
    keyboard.handler(_Event("up", "shift", 42))

    assert captured == []
