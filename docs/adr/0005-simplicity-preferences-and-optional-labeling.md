# Simplicity, Preferences Integration, and Optional Labeling

## Context
Following the core principle of simplicity and avoiding interface clutter, secondary features must remain unobtrusive while allowing flexible personalization.

## Decision
1. **Confined Configuration**: No items are added to NVDA's Tools menu; all settings reside strictly within the dedicated Tymer panel in NVDA Preferences.
2. **Built-in Audio**: Relies on clean, embedded default wave sounds without complex external file import mechanics.
3. **Optional Slot Labeling**: The `Control + N` dialog includes an optional label field; if empty, the slot defaults to "Timer N" / "المؤقت N".
4. **Parallel Speech Flow**: Expiry speech is dispatched through `ui.message` without invoking `speech.cancelSpeech()`, preserving ongoing reading or typing context.
5. **Configurable Pre-expiry Cue**: A setting is provided to enable or disable a discrete audio warning cue as zero approaches (default disabled).

## Status
Accepted
