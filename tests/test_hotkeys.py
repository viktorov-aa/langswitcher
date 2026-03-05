from langswitcher.hotkeys import KeyboardListener


def test_normalize_shift_scan_code_left() -> None:
    assert KeyboardListener._normalize_shift("shift", 42) == "left_shift"


def test_normalize_shift_scan_code_right() -> None:
    assert KeyboardListener._normalize_shift("shift", 54) == "right_shift"


def test_normalize_shift_alias_left() -> None:
    assert KeyboardListener._normalize_shift_alias("lshift") == "left_shift"


def test_normalize_shift_alias_right() -> None:
    assert KeyboardListener._normalize_shift_alias("shift_right") == "right_shift"
