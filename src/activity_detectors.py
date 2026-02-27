from typing import Callable, Optional
from time import monotonic
import logging
import platform

def build_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    if platform.system().lower() == "darwin":
        return _build_macos_activity_detectors(logger, position_getter)

    logger.warning("Keyboard activity detection unavailable; using mouse-only detection")
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


def _build_macos_activity_detectors(
    logger: logging.Logger,
    position_getter: Callable[[], object],
) -> tuple[Callable[[], float], Optional[Callable[[], float]]]:
    try:
        from Quartz import (
            CGEventSourceSecondsSinceLastEventType,
            kCGEventKeyDown,
            kCGEventLeftMouseDown,
            kCGEventLeftMouseUp,
            kCGEventMouseMoved,
            kCGEventRightMouseDown,
            kCGEventRightMouseUp,
            kCGEventScrollWheel,
            kCGEventSourceStateCombinedSessionState,
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