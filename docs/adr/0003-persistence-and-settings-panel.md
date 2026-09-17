# Persistence and Settings Panel

## Context
User preferences for countdown timers and behavior across NVDA restarts require a centralized, accessible configuration panel integrated into NVDA settings.

## Decision
1. A dedicated "Tymer" settings panel is registered in `gui.NVDASettingsDialog.categoryClasses`.
2. The panel provides options for:
   - Expiry notification style (Sound only, Speech only, Both sound and speech).
   - Command layer entry audio cue (Beep on/off).
   - NVDA restart behavior (Resume active countdowns, Reset/Discard, or Keep paused).
   - Configurable default durations for slots 1 through 5.
3. State is persisted in NVDA's configuration system (`config.conf["tymer"]`).

## Status
Accepted
