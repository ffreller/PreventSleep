from __future__ import annotations

import logging
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import monotonic, sleep
from typing import Optional

# Default key press configuration (adjust here, not via CLI)
DEFAULT_KEY_NAME = "f13"
DEFAULT_KEY_INTERVAL_MINUTES = 10.0


@dataclass(frozen=True)
class CliArgs:
    check_interval: float
    max_running_time: Optional[float]
    jiggle_pixels: int
    worker: bool

    def __post_init__(self) -> None:
        if self.check_interval <= 0:
            raise ValueError("--check-interval must be > 0")
        if self.max_running_time is not None and self.max_running_time <= 0:
            raise ValueError("--max-running-time must be > 0")
        if self.jiggle_pixels < 0:
            raise ValueError("--jiggle-pixels must be >= 0")


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
    jiggle_pixels: int = 1,
    key_name: str = DEFAULT_KEY_NAME,
    key_interval_minutes: float = DEFAULT_KEY_INTERVAL_MINUTES,
) -> None:
    from pyautogui import moveTo, position, press, size

    interval_seconds = check_interval_minutes * 60
    required_idle_seconds = interval_seconds
    jiggle_step = max(1, int(jiggle_pixels))
    key_interval_seconds = key_interval_minutes * 60

    start_time = monotonic()
    last_activity_time = monotonic()
    last_position = position()

    next_key_time = monotonic() + key_interval_seconds

    logger.info(
        "Started: interval=%ss required_idle=%ss jiggle=%spx key=%s key_interval=%smin",
        round(interval_seconds, 2),
        round(required_idle_seconds, 2),
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
        if idle_for < required_idle_seconds:
            logger.debug("Idle for %.2fs (required %.2fs); skipping", idle_for, required_idle_seconds)
            continue

        x, y = position()
        width, _ = size()
        target_x = x + jiggle_step
        if target_x >= width:
            target_x = max(0, x - jiggle_step)

        moveTo(target_x, y, duration=0)
        moveTo(x, y, duration=0)

        key_sent = False
        if now >= next_key_time:
            press(key_name)
            key_sent = True
            next_key_time = now + key_interval_seconds

        logger.info(
            "Synthetic input sent: jiggle_return at (%s,%s)%s",
            x,
            y,
            f", key={key_name}" if key_sent else "",
        )


def _append_if_not_none(cmd: list[str], flag: str, value: Optional[object]) -> None:
    if value is not None:
        cmd.extend([flag, str(value)])


def run_worker(args: CliArgs) -> int:
    logger = setup_logging(level="INFO")
    run_keep_awake(
        check_interval_minutes=args.check_interval,
        logger=logger,
        max_running_time_minutes=args.max_running_time,
        jiggle_pixels=max(1, args.jiggle_pixels),
        key_name=DEFAULT_KEY_NAME,
        key_interval_minutes=DEFAULT_KEY_INTERVAL_MINUTES,
    )
    return 0


def spawn_background(args: CliArgs) -> int:
    script_path = Path(__file__).resolve().parent.parent / "main.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--worker",
        "--check-interval",
        str(args.check_interval),
    ]

    _append_if_not_none(cmd, "--max-running-time", args.max_running_time)
    _append_if_not_none(cmd, "--jiggle-pixels", args.jiggle_pixels)

    if platform.system().lower() == "windows":
        creationflags = 0
        creationflags |= getattr(subprocess, "DETACHED_PROCESS", 0)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        process = subprocess.Popen(cmd, creationflags=creationflags, close_fds=True)
    else:
        with open(os.devnull, "rb") as devnull_in, open(os.devnull, "ab") as devnull_out:
            process = subprocess.Popen(
                cmd,
                stdin=devnull_in,
                stdout=devnull_out,
                stderr=devnull_out,
                start_new_session=True,
                close_fds=True,
            )

    print(f"Started background keep-awake process PID={process.pid}")
    return 0
