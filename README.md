# PreventSleep

Minimal script to keep apps from treating the PC as idle.

How it works:
- Checks every `--check-interval` minutes.
- If the user is idle long enough, it sends minimal synthetic input:
  - tiny mouse jiggle + return to original position
  - low-frequency harmless key press (enabled by default)
- If user activity is detected (mouse/keyboard), that cycle is skipped, and in-progress synthetic input is aborted for the cycle.
- Runs in foreground by default (stop with `Ctrl+C`).
- Optional detached background mode via `--background`.

Default key press config lives in `src/helpers.py`:
- `DEFAULT_KEY_NAME` (default: `f13`)
- `DEFAULT_KEY_INTERVAL_MINUTES` (default: `10`)

## Install

```bash
uv sync
```

Linux only: install `xprintidle` to enable keyboard + mouse idle detection.
Without it, the script falls back to mouse-only idle detection.

## Usage

```bash
uv run python main.py --check-interval 2
```

The command stays attached to your terminal. Press `Ctrl+C` to stop it.

## Useful options

- `--check-interval` (required): minutes between checks.
- `--max-running-time`: optional total runtime in minutes.
- `--jiggle-pixels`: jiggle size in pixels (default: `10`).
- `--background`: run detached and return immediately.

## Examples

Minimal:

```bash
uv run python main.py --check-interval 2
```

Run for 30 minutes:

```bash
uv run python main.py --check-interval 1 --max-running-time 30
```

Run detached in background:

```bash
uv run python main.py --check-interval 2 --background
```

In background mode, stop the process from your OS process manager (Task Manager / Activity Monitor / `kill`).
