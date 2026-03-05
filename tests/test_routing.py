from langswitcher.routing import ShiftKeyRouter


def test_left_shift_routes_to_english() -> None:
    router = ShiftKeyRouter(hotkey_map={"left_shift": "en", "right_shift": "ru"})
    assert router.route_event("left shift") == "en"
