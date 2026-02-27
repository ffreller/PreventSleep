# PreventSleep

Minimal script to keep apps from treating the PC as idle.

How it works:
- Checks every `--check-interval` minutes.
- If the user is idle long enough, it sends minimal synthetic input:
  - tiny mouse jiggle + return to original position
  - low-frequency harmless key press (enabled by default)
- Runs in background (detached process) when started.

Default key press config lives in `src/helpers.py`:
- `DEFAULT_KEY_NAME` (default: `f13`)
- `DEFAULT_KEY_INTERVAL_MINUTES` (default: `10`)

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
- `--jiggle-pixels`: jiggle size in pixels (default: `10`).

## Examples

Minimal:

```bash
uv run python main.py --check-interval 2
```

Run for 30 minutes:

```bash
uv run python main.py --check-interval 1 --max-running-time 30
```

Stop the background process from your OS process manager (Task Manager / Activity Monitor / `kill`).
