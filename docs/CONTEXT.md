# Instant Timer

Instant Timer is an NVDA screen reader add-on providing five independent, customizable countdown timers operated through a dedicated modal command layer, engineered on principles of simplicity and non-complexity.

## Language

**Command Layer**:
A temporary modal input state entered via a designated gesture, in which numerical keys execute actions on timer slots.
_Avoid_: Hotkey mode, sub-menu, layer state

**Layer Trigger**:
The global NVDA shortcut (`NVDA+E`) that transitions the input subsystem into the Command Layer.
_Avoid_: Activation key, master hotkey

**Countdown Timer**:
An independent time tracker counting downward from a defined duration to zero.
_Avoid_: Stopwatch, alarm, clock

**Slot**:
One of the five distinct numbered positions (1 to 5) assigned to an independent countdown timer.
_Avoid_: Index, channel, timer number

**Slot Label**:
An optional descriptive name assigned to a slot, defaulting to its canonical number when blank.
_Avoid_: Alias, tag, custom name

**Quad Action**:
The four standardized operations mapped to each Slot using no modifier, Shift, Control, or Alt.
_Avoid_: Multi-action, sub-command

**Expiry Notification**:
The sensory signal emitted when a timer reaches zero, defaulting to an audio wave sound with configurable speech feedback.
_Avoid_: Ring, chime, alert message

**Parallel Notification**:
The non-interrupting dispatch of spoken expiry messages alongside active screen reader speech.
_Avoid_: Background message, silent speech

**Alarm Preemption**:
The immediate termination of any ongoing alarm sound whenever a subsequent timer completes its countdown.
_Avoid_: Audio interruption, ringer override

**Pre-expiry Cue**:
An optional discrete audio signal sounded shortly prior to reaching zero.
_Avoid_: Early alarm, warning beep

**Verbosity Mode**:
The configurable depth of spoken messages, toggled between Beginner (explanatory) and Advanced (concise).
_Avoid_: Verbosity level, talkativeness

**Auxiliary Layer Key**:
A non-slot key within the command layer mapped to global utility operations (H for help, Space for silencing alarms, A for reporting status).
_Avoid_: Global hotkey, extra command

**Alarm Dismissal**:
The manual or automatic silencing of an active expiry notification sound, accessible exclusively via the Space key within the Command Layer.
_Avoid_: Stopping alarm, turning off ringer

**Restart Persistence**:
The configurable policy determining whether active countdowns resume, reset, or pause when NVDA is restarted.
_Avoid_: Session recovery, reload behavior

**Settings Panel**:
A dedicated preferences category registered under NVDA Settings allowing full graphical configuration of Instant Timer.
_Avoid_: Options page, config window
