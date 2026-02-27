from __future__ import annotations

import os
import platform
import subprocess
import sys
from argparse import SUPPRESS, ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import Optional

from funcs import run_keep_awake, setup_logging


def positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ArgumentTypeError("must be a number") from exc
    if parsed <= 0:
        raise ArgumentTypeError("must be > 0")
    return parsed


def non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ArgumentTypeError("must be a number") from exc
    if parsed < 0:
        raise ArgumentTypeError("must be >= 0")
    return parsed


def non_negative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise ArgumentTypeError("must be >= 0")
    return parsed


def parse_args() -> object:
    parser = ArgumentParser(description="Minimal keep-awake script using tiny synthetic input")

    parser.add_argument(
        "--check-interval",
        "--check_interval",
        dest="check_interval",
        required=True,
        type=positive_float,
        help="Minutes between checks (required).",
    )
    parser.add_argument(
        "--max-running-time",
        "--max_running_time",
        dest="max_running_time",
        type=positive_float,
        default=None,
        help="Optional total runtime in minutes.",
    )
    parser.add_argument(
        "--idle-threshold",
        type=non_negative_float,
        default=None,
        help="Idle seconds required before synthetic input. Default: check_interval*60.",
    )
    parser.add_argument(
        "--jiggle-pixels",
        type=non_negative_int,
        default=1,
        help="Small mouse move distance in pixels (default: 1).",
    )
    parser.add_argument(
        "--key-name",
        type=str,
        default=None,
        help="Optional harmless key press for app idle checks (example: shift).",
    )
    parser.add_argument(
        "--key-interval",
        type=positive_float,
        default=None,
        help="Minutes between key presses (required if --key-name is set).",
    )
    parser.add_argument("--worker", action="store_true", help=SUPPRESS)

    args = parser.parse_args()

    if args.key_name and args.key_interval is None:
        parser.error("--key-interval is required when --key-name is set")
    if args.key_interval is not None and not args.key_name:
        parser.error("--key-name is required when --key-interval is set")

    return args


def _append_if_not_none(cmd: list[str], flag: str, value: Optional[object]) -> None:
    if value is not None:
        cmd.extend([flag, str(value)])


def run_worker(args: object) -> int:
    logger = setup_logging(level="INFO")
    run_keep_awake(
        check_interval_minutes=args.check_interval,
        logger=logger,
        max_running_time_minutes=args.max_running_time,
        idle_threshold_seconds=args.idle_threshold,
        jiggle_pixels=max(1, args.jiggle_pixels),
        key_name=args.key_name,
        key_interval_minutes=args.key_interval,
    )
    return 0


def spawn_background(args: object) -> int:
    script_path = Path(__file__).resolve()
    cmd = [
        sys.executable,
        str(script_path),
        "--worker",
        "--check-interval",
        str(args.check_interval),
    ]

    _append_if_not_none(cmd, "--max-running-time", args.max_running_time)
    _append_if_not_none(cmd, "--idle-threshold", args.idle_threshold)
    _append_if_not_none(cmd, "--jiggle-pixels", args.jiggle_pixels)
    _append_if_not_none(cmd, "--key-name", args.key_name)
    _append_if_not_none(cmd, "--key-interval", args.key_interval)

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


def main() -> int:
    args = parse_args()
    if args.worker:
        return run_worker(args)
    return spawn_background(args)


if __name__ == "__main__":
    raise SystemExit(main())
