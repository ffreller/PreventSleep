# PreventSleep

Minimal script to keep apps from treating the PC as idle.

How it works:
- Checks every `--check-interval` minutes.
- If the user is idle long enough, it sends minimal synthetic input:
  - tiny mouse jiggle + return to original position
  - optional low-frequency harmless key press

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py --check-interval 2
```

## Useful options

- `--check-interval` (required): minutes between checks.
- `--max-running-time`: optional total runtime in minutes.
- `--idle-threshold`: idle seconds needed before sending synthetic input (default: `check_interval * 60`).
- `--jiggle-pixels`: jiggle size in pixels (default: `1`).
- `--key-name`: optional key (example: `shift`).
- `--key-interval`: minutes between key presses (required with `--key-name`).
- `--log-level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- `--log-file`: optional file path for logs.

## Examples

Minimal:

```bash
python main.py --check-interval 2
```

For strict app idle checks:

```bash
python main.py --check-interval 1 --idle-threshold 60 --key-name shift --key-interval 10
```

Stop with `Ctrl+C`.
