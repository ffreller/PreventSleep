# PreventSleep

Minimal script to keep apps from treating the PC as idle.

How it works:
- Checks every `--check-interval` minutes.
- If the user is idle long enough, it sends minimal synthetic input:
  - tiny mouse jiggle + return to original position
  - optional low-frequency harmless key press
- Runs in background (detached process) when started.

## Install

```bash
uv sync
```

## Usage

```bash
uv run python main.py --check-interval 2
```

The command immediately returns and leaves the keep-awake process running in background.

## Useful options

- `--check-interval` (required): minutes between checks.
- `--max-running-time`: optional total runtime in minutes.
- `--idle-threshold`: idle seconds needed before sending synthetic input (default: `check_interval * 60`).
- `--jiggle-pixels`: jiggle size in pixels (default: `1`).
- `--key-name`: optional key (example: `shift`).
- `--key-interval`: minutes between key presses (required with `--key-name`).

## Examples

Minimal:

```bash
uv run python main.py --check-interval 2
```

For strict app idle checks:

```bash
uv run python main.py --check-interval 1 --idle-threshold 60 --key-name shift --key-interval 10
```

Stop the background process from your OS process manager (Task Manager / Activity Monitor / `kill`).
