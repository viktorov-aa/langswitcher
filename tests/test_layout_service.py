from __future__ import annotations

from langswitcher.layout_service import WindowsLayoutService


class _FakeUser32:
    def __init__(self, foreground: int = 100, current_hkl: int = 0x0409) -> None:
        self.foreground = foreground
        self.current_hkl = current_hkl
        self.load_calls: list[tuple[str, int]] = []
        self.post_calls: list[tuple[int, int, int, int]] = []
        self.activate_calls: list[tuple[int, int]] = []

    def LoadKeyboardLayoutW(self, layout_id: str, flags: int) -> int:  # noqa: N802
        self.load_calls.append((layout_id, flags))
        return int(layout_id, 16)

    def GetForegroundWindow(self) -> int:  # noqa: N802
        return self.foreground

    def GetWindowThreadProcessId(self, hwnd: int, process_id) -> int:  # noqa: N802
        return hwnd + 1

    def GetKeyboardLayout(self, thread_id: int) -> int:  # noqa: N802
        return self.current_hkl

    def PostMessageW(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:  # noqa: N802
        self.post_calls.append((hwnd, msg, wparam, lparam))
        self.current_hkl = lparam
        return 1

    def ActivateKeyboardLayout(self, hkl: int, flags: int) -> int:  # noqa: N802
        self.activate_calls.append((hkl, flags))
        self.current_hkl = hkl
        return 1


def test_apply_layout_posts_to_foreground_window(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=777, current_hkl=0x0419)
    service._user32 = fake

    changed = service.apply_layout("en")

    assert changed is True
    assert fake.load_calls == [("00000409", service.KLF_ACTIVATE)]
    assert fake.post_calls == [(777, service.WM_INPUTLANGCHANGEREQUEST, 0, 0x00000409)]
    assert fake.activate_calls == []
    assert service._last_applied == "en"


def test_apply_layout_falls_back_to_activate_when_no_foreground(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=0, current_hkl=0x0409)
    service._user32 = fake

    changed = service.apply_layout("ru")

    assert changed is True
    assert fake.load_calls == [("00000419", service.KLF_ACTIVATE)]
    assert fake.post_calls == []
    assert fake.activate_calls == [(0x00000419, 0)]
    assert service._last_applied == "ru"


def test_apply_layout_returns_false_only_when_target_is_currently_active(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=777, current_hkl=0x0409)
    service._user32 = fake
    service._last_applied = "ru"

    changed = service.apply_layout("en")

    assert changed is False
    assert fake.load_calls == []
    assert fake.post_calls == []
    assert service._last_applied == "en"


def test_apply_layout_switches_again_after_external_layout_change(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=777, current_hkl=0x0419)
    service._user32 = fake

    first_changed = service.apply_layout("en")
    fake.current_hkl = 0x0419
    second_changed = service.apply_layout("en")

    assert first_changed is True
    assert second_changed is True
    assert fake.load_calls == [
        ("00000409", service.KLF_ACTIVATE),
        ("00000409", service.KLF_ACTIVATE),
    ]
    assert fake.post_calls == [
        (777, service.WM_INPUTLANGCHANGEREQUEST, 0, 0x00000409),
        (777, service.WM_INPUTLANGCHANGEREQUEST, 0, 0x00000409),
    ]
    assert service._last_applied == "en"
