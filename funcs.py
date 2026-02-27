from __future__ import annotations

import logging
from time import monotonic, sleep
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("prevent_sleep")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def run_keep_awake(
    check_interval_minutes: float,
    logger: logging.Logger,
    max_running_time_minutes: Optional[float] = None,
    idle_threshold_seconds: Optional[float] = None,
    jiggle_pixels: int = 1,
    key_name: Optional[str] = None,
    key_interval_minutes: Optional[float] = None,
) -> None:
    from pyautogui import moveTo, position, press, size

    interval_seconds = check_interval_minutes * 60
    idle_threshold = idle_threshold_seconds if idle_threshold_seconds is not None else interval_seconds
    jiggle_step = max(1, int(jiggle_pixels))

    start_time = monotonic()
    last_activity_time = monotonic()
    last_position = position()

    next_key_time: Optional[float] = None
    if key_name and key_interval_minutes:
        next_key_time = monotonic() + (key_interval_minutes * 60)

    logger.info(
        "Started: interval=%ss idle_threshold=%ss jiggle=%spx key=%s key_interval=%smin",
        round(interval_seconds, 2),
        round(idle_threshold, 2),
        jiggle_step,
        key_name,
        key_interval_minutes,
    )

    while True:
        sleep(interval_seconds)
        now = monotonic()

        if max_running_time_minutes is not None:
            if now - start_time >= (max_running_time_minutes * 60):
                logger.info("Stopping: max running time reached")
                return

        current_position = position()
        if current_position != last_position:
            last_position = current_position
            last_activity_time = now
            logger.debug("User active; skipping synthetic input")
            continue

        idle_for = now - last_activity_time
        if idle_for < idle_threshold:
            logger.debug("Idle for %.2fs (threshold %.2fs); skipping", idle_for, idle_threshold)
            continue

        x, y = position()
        width, _ = size()
        target_x = x + jiggle_step
        if target_x >= width:
            target_x = max(0, x - jiggle_step)

        moveTo(target_x, y, duration=0)
        moveTo(x, y, duration=0)

        key_sent = False
        if key_name and next_key_time is not None and now >= next_key_time:
            press(key_name)
            key_sent = True
            next_key_time = now + (key_interval_minutes * 60)

        logger.info(
            "Synthetic input sent: jiggle_return at (%s,%s)%s",
            x,
            y,
            f", key={key_name}" if key_sent else "",
        )
