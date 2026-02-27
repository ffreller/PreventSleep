import logging
import platform
import shutil
import subprocess
from time import monotonic
from typing import Callable, Optional


def build_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    system = platform.system().lower()

    if system == "darwin":
        return _build_macos_activity_detectors(logger, position_getter)

    if system == "windows":
        return _build_windows_activity_detectors(logger, position_getter)

    if system == "linux":
        return _build_linux_activity_detectors(logger, position_getter)

    logger.warning("Unsupported platform '%s'; using mouse-only activity detection", system)
    return _build_mouse_only_idle_detector(position_getter), None


def _build_mouse_only_idle_detector(position_getter: Callable[[], object]) -> Callable[[], float]:
    last_position = position_getter()
    last_activity_time = monotonic()

    def mouse_idle_seconds() -> float:
        nonlocal last_position, last_activity_time
        now = monotonic()
        current_position = position_getter()
        if current_position != last_position:
            last_position = current_position
            last_activity_time = now
        return max(0.0, now - last_activity_time)

    return mouse_idle_seconds


def _build_windows_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    try:
        import ctypes
        from ctypes import wintypes
    except Exception as exc:  # pragma: no cover - platform/runtime specific
        logger.warning("Windows input detection unavailable (%s); using mouse-only detection", exc)
        return _build_mouse_only_idle_detector(position_getter), None

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
    user32.GetLastInputInfo.restype = wintypes.BOOL
    kernel32.GetTickCount.restype = wintypes.DWORD

    mouse_idle_seconds = _build_mouse_only_idle_detector(position_getter)
    use_mouse_fallback = False

    def windows_idle_seconds() -> float:
        nonlocal use_mouse_fallback
        if use_mouse_fallback:
            return mouse_idle_seconds()

        try:
            info = LASTINPUTINFO()
            info.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if not user32.GetLastInputInfo(ctypes.byref(info)):
                raise ctypes.WinError()

            now_ms = kernel32.GetTickCount()
            idle_ms = (now_ms - info.dwTime) & 0xFFFFFFFF
            return max(0.0, idle_ms / 1000.0)
        except Exception as exc:
            use_mouse_fallback = True
            logger.warning(
                "Windows idle detection failed (%s); falling back to mouse-only detection",
                exc,
            )
            return mouse_idle_seconds()

    logger.info("Using Windows keyboard + mouse activity detection")
    return windows_idle_seconds, None


def _build_linux_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    xprintidle_path = shutil.which("xprintidle")
    if xprintidle_path is None:
        logger.warning("xprintidle not found; using mouse-only activity detection")
        return _build_mouse_only_idle_detector(position_getter), None

    mouse_idle_seconds = _build_mouse_only_idle_detector(position_getter)
    use_mouse_fallback = False

    def linux_idle_seconds() -> float:
        nonlocal use_mouse_fallback
        if use_mouse_fallback:
            return mouse_idle_seconds()

        try:
            result = subprocess.run(
                [xprintidle_path],
                check=True,
                capture_output=True,
                text=True,
            )
            return max(0.0, float(result.stdout.strip()) / 1000.0)
        except Exception as exc:
            use_mouse_fallback = True
            logger.warning(
                "Linux idle detection via xprintidle failed (%s); falling back to mouse-only detection",
                exc,
            )
            return mouse_idle_seconds()

    logger.info("Using Linux keyboard + mouse activity detection via xprintidle")
    return linux_idle_seconds, None


def _build_macos_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    try:
        from Quartz import (
            CGEventSourceSecondsSinceLastEventType, #type: ignore
            kCGEventKeyDown, #type: ignore
            kCGEventLeftMouseDown, #type: ignore
            kCGEventLeftMouseUp, #type: ignore
            kCGEventMouseMoved, #type: ignore
            kCGEventRightMouseDown, #type: ignore
            kCGEventRightMouseUp, #type: ignore
            kCGEventScrollWheel, #type: ignore
            kCGEventSourceStateCombinedSessionState, #type: ignore
        )
    except Exception as exc:  # pragma: no cover - platform/runtime specific
        logger.warning("macOS input detection unavailable (%s); using mouse-only detection", exc)
        return _build_mouse_only_idle_detector(position_getter), None

    monitored_event_types = (
        kCGEventMouseMoved,
        kCGEventLeftMouseDown,
        kCGEventLeftMouseUp,
        kCGEventRightMouseDown,
        kCGEventRightMouseUp,
        kCGEventScrollWheel,
        kCGEventKeyDown,
    )

    def seconds_since(event_type: int) -> float:
        return float(
            CGEventSourceSecondsSinceLastEventType(
                kCGEventSourceStateCombinedSessionState,
                event_type,
            )
        )

    def macos_idle_seconds() -> float:
        return min(seconds_since(event_type) for event_type in monitored_event_types)

    def macos_last_key_event_time() -> float:
        return monotonic() - seconds_since(kCGEventKeyDown)

    logger.info("Using macOS mouse + keyboard activity detection")
    return macos_idle_seconds, macos_last_key_event_time
