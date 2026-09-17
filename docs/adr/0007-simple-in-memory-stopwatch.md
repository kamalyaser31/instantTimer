# Simple In-Memory Stopwatch Architecture

## Context
Users frequently require a quick, lightweight count-up stopwatch to track task duration alongside fixed countdown timers, without introducing persistent configuration overhead or conflicting with NVDA global shortcuts.

## Decision
1. **Layer Integration**: The stopwatch is accessed exclusively within the existing `NVDA+Y` modal layer via key `S`.
2. **Quad-Modifier Symmetry**:
   - `S`: Start (if stopped) or Query elapsed time (if running/paused).
   - `Shift + S`: Pause or Resume stopwatch.
   - `Control + S`: Immediate restart from zero (Reset and Start).
   - `Alt + S`: Reset to zero and stop (Reset and Stop).
3. **Ultra-Concise Digital Format**:
   - Elapsed time is spoken in compact digital string format: `MM:SS` when under one hour, and `HH:MM:SS` upon reaching one hour.
   - Status prompts are strictly concise: "Started", "Paused", "Resumed", "Restarted", "Reset", and "{time}, paused".
4. **Distinct Tone Feedback**:
   - Start / Restart: Rising double tone (440Hz -> 660Hz).
   - Pause: Low tone (400Hz).
   - Resume: Mid tone (600Hz).
   - Reset: Descending double tone (350Hz -> 250Hz).
5. **In-Memory Lifetime**:
   - State is purely ephemeral; restarts of NVDA reset the stopwatch to stopped zero without modifying configuration files.
6. **Independence of Report A**:
   - Key `A` inside the layer continues to report only the 5 countdown timer slots to preserve brevity.

## Status
Accepted
