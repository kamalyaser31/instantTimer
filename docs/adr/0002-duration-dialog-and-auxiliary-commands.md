# Duration Dialog and Auxiliary Commands

## Context
Configuring countdown durations and controlling alarms inside the command layer must be fast, keyboard-friendly, and accessible without visual friction.

## Decision
1. Duration input for `Control + N` provides a choice list of common presets (5, 10, 15, 20, 30, 45, 60 minutes) alongside a custom manual entry option (hours, minutes, seconds).
2. Alarm notifications play an embedded WAV wave file for up to 5 seconds before silencing automatically, with immediate dismissal on demand.
3. The command layer includes three auxiliary commands:
   - `H`: Displays the layer command reference in NVDA browse mode.
   - `Space`: Immediately silences an active alarm.
   - `A`: Announces the comprehensive status of all five timer slots.

## Status
Accepted
