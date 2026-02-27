from __future__ import annotations

from argparse import ArgumentParser, ArgumentTypeError

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
    parser.add_argument("--log-level", default="INFO", help="DEBUG, INFO, WARNING, ERROR")

    args = parser.parse_args()

    if args.key_name and args.key_interval is None:
        parser.error("--key-interval is required when --key-name is set")
    if args.key_interval is not None and not args.key_name:
        parser.error("--key-name is required when --key-interval is set")

    return args


def main() -> int:
    args = parse_args()
    logger = setup_logging(level=args.log_level)

    try:
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
    except KeyboardInterrupt:
        logger.info("Ctrl+C received. Stopping.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
