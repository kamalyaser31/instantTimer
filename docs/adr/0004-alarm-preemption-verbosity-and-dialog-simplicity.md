# Alarm Preemption, Verbosity Levels, and Dialog Simplicity

## Context
Handling concurrent timer expiries, user feedback verbosity, duration setting interaction, and ringer dismissal requires predictable, accessible behaviors tailored to blind users.

## Decision
1. **Alarm Preemption**: When a timer reaches zero while a previous alarm sound is still playing, the newer alarm immediately cuts off and replaces the previous alarm audio.
2. **Verbosity Levels**: Added a configuration setting for status announcements:
   - *Beginner* (default): Descriptive sentences including slot number, time, status, and instructional prompts.
   - *Advanced*: Concise announcements delivering only essential time and status.
3. **Duration Setting Dialog**: Eliminated preset dropdown lists; the `Control + N` dialog exclusively presents three standard spin/text fields (Hours, Minutes, Seconds) with default focus on Minutes.
4. **Layer-Restricted Dismissal**: Active alarms are dismissed exclusively from within the command layer using `Space` (`NVDA+Y` then `Space`), or automatically upon the 1-second playback timeout.
5. **Static Speech Compliance**: The add-on strictly respects the user's active NVDA speech mode without forcibly escalating on-demand or muted modes to talk.

## Status
Accepted
