from __future__ import annotations

from langswitcher.layout_service import WindowsLayoutService


class _FakeUser32:
    def __init__(self, foreground: int = 100) -> None:
        self.foreground = foreground
        self.load_calls: list[tuple[str, int]] = []
        self.post_calls: list[tuple[int, int, int, int]] = []
        self.activate_calls: list[tuple[int, int]] = []

    def LoadKeyboardLayoutW(self, layout_id: str, flags: int) -> int:  # noqa: N802
        self.load_calls.append((layout_id, flags))
        return 12345

    def GetForegroundWindow(self) -> int:  # noqa: N802
        return self.foreground

    def PostMessageW(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:  # noqa: N802
        self.post_calls.append((hwnd, msg, wparam, lparam))
        return 1

    def ActivateKeyboardLayout(self, hkl: int, flags: int) -> int:  # noqa: N802
        self.activate_calls.append((hkl, flags))
        return 1


def test_apply_layout_posts_to_foreground_window(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=777)
    service._user32 = fake

    changed = service.apply_layout("en")

    assert changed is True
    assert fake.load_calls == [("00000409", service.KLF_ACTIVATE)]
    assert fake.post_calls == [(777, service.WM_INPUTLANGCHANGEREQUEST, 0, 12345)]
    assert fake.activate_calls == []


def test_apply_layout_falls_back_to_activate_when_no_foreground(monkeypatch) -> None:
    monkeypatch.setattr("langswitcher.layout_service.os.name", "nt")
    service = WindowsLayoutService()
    fake = _FakeUser32(foreground=0)
    service._user32 = fake

    changed = service.apply_layout("ru")

    assert changed is True
    assert fake.load_calls == [("00000419", service.KLF_ACTIVATE)]
    assert fake.post_calls == []
    assert fake.activate_calls == [(12345, 0)]
