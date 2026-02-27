from __future__ import annotations
from argparse import SUPPRESS, ArgumentParser
from src.helpers import CliArgs, run_worker, spawn_background


def parse_args() -> CliArgs:
    parser = ArgumentParser(
        description="Minimal keep-awake script using tiny synthetic input"
    )

    parser.add_argument(
        "--check-interval",
        "--check_interval",
        dest="check_interval",
        required=False,
        default=5,
        type=float,
        help="Minutes between checks (required).",
    )
    parser.add_argument(
        "--max-running-time",
        "--max_running_time",
        dest="max_running_time",
        type=float,
        default=None,
        help="Optional total runtime in minutes.",
    )
    parser.add_argument(
        "--jiggle-pixels",
        type=int,
        default=10,
        help="Small mouse move distance in pixels (default: 10).",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run detached in background (default is foreground, cancellable with Ctrl+C).",
    )
    parser.add_argument("--worker", action="store_true", help=SUPPRESS)

    args = parser.parse_args()

    return CliArgs(
        check_interval=args.check_interval,
        max_running_time=args.max_running_time,
        jiggle_pixels=args.jiggle_pixels,
        worker=args.worker,
        background=args.background,
    )


def main() -> int:
    args = parse_args()
    if args.worker or not args.background:
        return run_worker(args)
    return spawn_background(args)


if __name__ == "__main__":
    raise SystemExit(main())
