# Quick One-Time Timer Architecture

## Context
Users frequently need an ad-hoc, one-off countdown timer for custom durations (e.g. 7 minutes for boiling tea, 45 minutes for a task) without altering or overriding their 5 pre-configured persistent countdown slots.

## Decision
1. **Layer Integration**: The quick timer is accessed exclusively within the existing `NVDA+Y` modal layer via key `Q`.
2. **Quad-Modifier Symmetry**:
   - `Q`: If stopped, opens `QuickDurationDialog` directly and starts immediately upon confirmation. If running or paused, queries and reports remaining time.
   - `Control + Q`: Always opens `QuickDurationDialog` to configure a new duration and starts immediately upon confirmation.
   - `Shift + Q`: Pause or Resume the quick timer.
   - `Alt + Q`: Reset the quick timer to stopped state and silence any active alarm.
3. **Dedicated In-Memory Slot**:
   - Implemented as a dedicated `quickSlot` (`TimerSlot` with index 0 or labeled "Quick timer") inside `CountdownEngine`.
   - Purely in-memory; not serialized to NVDA configuration files (`config.conf`).
4. **Quick Duration Dialog**:
   - Dedicated dialog (`QuickDurationDialog`) focused directly on the Minutes field.
   - Contains only Hours, Minutes, and Seconds controls (no label field) for rapid input.
   - Remembers the last entered quick duration during the current session.
   - If opened via `Control+Q` while a quick timer is actively running, temporarily pauses the countdown; if the dialog is canceled/dismissed, it resumes automatically; if confirmed, replaces the duration and starts immediately.
5. **Reporting and Expiry Integration**:
   - Seamlessly integrated with engine ticker, 10-second pre-expiry cue (if enabled), and alarm trigger on expiry with automatic reset to stopped.
   - Key `A` (`reportAllStatus`) includes the quick timer only when it is active (`running` or `paused`), keeping reports clean when idle.

## Status
Accepted
