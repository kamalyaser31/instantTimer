# Core Layer and Timer Architecture

## Context
Tymer requires an accessible, low-latency mechanism in NVDA to control five countdown timers without conflicting with standard screen reader hotkeys or trapping user keyboard input.

## Decision
We adopt the one-shot modal command layer pattern triggered via `NVDA+Y`, dynamically binding keyboard slots 1 to 5 with a balanced quad modifier scheme:
- `N` (1 to 5): Query remaining time or start if inactive.
- `Shift + N`: Pause or resume countdown.
- `Control + N`: Open duration configuration dialog.
- `Alt + N`: Reset and cancel timer.
Default timer durations are graduated (5, 10, 15, 25, 60 minutes). Expiry notification defaults to sound-only, with user options in the settings panel to enable speech or combined notification.

## Status
Accepted
