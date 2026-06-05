"""Platform-aware serial-port discovery helpers."""

from __future__ import annotations

import glob
import os
import platform
from typing import Iterable, Optional


LINUX_ALL_CANDIDATE_PATTERNS: tuple[str, ...] = (
    "/dev/serial/by-id/*",
    "/dev/serial/by-path/*",
    "/dev/ttyUSB*",
    "/dev/ttyACM*",
    "/dev/ttyAMA*",
    "/dev/ttyTHS*",
    "/dev/ttyS*",
)

LINUX_USB_ONLY_PATTERNS: tuple[str, ...] = (
    "/dev/serial/by-id/usb-*",
    "/dev/serial/by-path/*-usb-*/**",
    "/dev/ttyACM*",
    "/dev/ttyUSB*",
)

MACOS_USB_SERIAL_PATTERNS: tuple[str, ...] = (
    "/dev/cu.usbserial*",
    "/dev/cu.usbmodem*",
    "/dev/cu.SLAB_USBtoUART*",
    "/dev/cu.wchusbserial*",
    "/dev/cu.CH34*",
)


def is_macos() -> bool:
    return platform.system() == "Darwin"


def serial_candidate_patterns(*, include_uart: bool = False) -> tuple[str, ...]:
    if is_macos():
        return MACOS_USB_SERIAL_PATTERNS
    if include_uart:
        return LINUX_ALL_CANDIDATE_PATTERNS
    return LINUX_USB_ONLY_PATTERNS


def _append_candidate(candidates: list[str], seen_realpaths: set[str], path: str) -> None:
    try:
        realpath = os.path.realpath(path)
    except OSError:
        return
    if realpath in seen_realpaths:
        return
    if not os.path.exists(realpath):
        return
    seen_realpaths.add(realpath)
    candidates.append(path)


def glob_serial_candidates(patterns: Iterable[str]) -> list[str]:
    candidates: list[str] = []
    seen_realpaths: set[str] = set()
    for pattern in patterns:
        for path in sorted(glob.glob(pattern, recursive=True)):
            _append_candidate(candidates, seen_realpaths, path)
    return candidates


def _list_port_is_candidate(device: str, port: object, *, include_uart: bool) -> bool:
    device_lower = device.lower()
    if is_macos():
        if not device.startswith("/dev/cu."):
            return False
        if getattr(port, "vid", None) is not None:
            return True
        return any(token in device_lower for token in ("usb", "serial", "slab", "wch", "ch34", "modem"))

    if include_uart:
        return device.startswith("/dev/")

    if getattr(port, "vid", None) is not None:
        return True
    return (
        device.startswith("/dev/ttyUSB")
        or device.startswith("/dev/ttyACM")
        or device.startswith("/dev/serial/by-id/usb-")
    )


def list_ports_candidates(*, include_uart: bool = False) -> list[str]:
    try:
        from serial.tools import list_ports
    except Exception:
        return []

    candidates: list[str] = []
    seen_realpaths: set[str] = set()
    for port in list_ports.comports():
        device = getattr(port, "device", None)
        if not device or not _list_port_is_candidate(device, port, include_uart=include_uart):
            continue
        _append_candidate(candidates, seen_realpaths, device)
    return candidates


def serial_candidate_devices(*, include_uart: bool = False) -> list[str]:
    candidates: list[str] = []
    seen_realpaths: set[str] = set()
    for path in glob_serial_candidates(serial_candidate_patterns(include_uart=include_uart)):
        _append_candidate(candidates, seen_realpaths, path)
    for path in list_ports_candidates(include_uart=include_uart):
        _append_candidate(candidates, seen_realpaths, path)
    return candidates


def default_serial_port() -> Optional[str]:
    if is_macos():
        candidates = serial_candidate_devices()
        return candidates[0] if candidates else None
    return "/dev/ttyUSB0"
