"""HEBI Mobile I/O discovery and input helpers."""

from __future__ import annotations

import time
from typing import Any

from .hebi_models import BridgeConfig, PhonePose


def _import_hebi():
    try:
        import hebi  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing optional dependency 'hebi-py'. Install it with "
            "`uv pip install -e '.[phone]'` or `pip install hebi-py`."
        ) from exc
    return hebi


def _create_mobile_io(config: BridgeConfig):
    hebi = _import_hebi()
    lookup = hebi.Lookup()
    if config.lookup_wait_s > 0:
        time.sleep(config.lookup_wait_s)

    if config.list_devices:
        print("[HEBI] Discovered devices:")
        for entry in lookup.entrylist:
            family = getattr(entry, "family", "?")
            name = getattr(entry, "name", "?")
            ip = getattr(entry, "ip_address", "?")
            print(f"  - family={family!r} name={name!r} ip={ip}")

    mobile_io = hebi.util.create_mobile_io(
        lookup,
        family=config.family,
        name=config.name,
    )
    if mobile_io is None:
        raise RuntimeError(
            f"Could not find HEBI Mobile I/O family={config.family!r} "
            f"name={config.name!r}. Open the app on the same LAN and check "
            "the iOS Mobile I/O settings."
        )

    if config.setup_mobile_ui:
        try:
            mobile_io.resetUI()
            mobile_io.add_text("B1: hold to move", blocking=False)
            mobile_io.add_text("Release + hold B1 again: recenter", blocking=False)
            mobile_io.add_text("B2/B4: gripper open/close", blocking=False)
            mobile_io.add_text("B8: quit bridge", blocking=False)
        except Exception as exc:
            print(f"[HEBI] UI setup skipped: {exc}")

    return mobile_io


def _read_button_state(mobile_io: Any, button_index: int) -> bool:
    if button_index <= 0:
        return False
    try:
        return bool(mobile_io.get_button_state(button_index))
    except Exception:
        return False


def _gripper_button_axis(mobile_io: Any, config: BridgeConfig) -> float:
    open_held = _read_button_state(mobile_io, config.gripper_open_button)
    close_held = _read_button_state(mobile_io, config.gripper_close_button)
    if open_held == close_held:
        return 0.0
    return 1.0 if open_held else -1.0


def _read_phone_pose(mobile_io: Any, config: BridgeConfig) -> PhonePose | None:
    try:
        return PhonePose.from_hebi(
            mobile_io.position,
            mobile_io.orientation,
            quaternion_order=config.quaternion_order,
        )
    except Exception:
        return None
