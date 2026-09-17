# Tymer - Countdown Timer Add-on for NVDA

**Tymer** is an accessible, efficient countdown timer add-on for the NVDA screen reader. It provides 5 independent countdown timer slots operated via a dedicated one-shot modal command layer.

## Key Features

- **One-Shot Modal Command Layer**: Triggered via `NVDA+Y`. The layer safely handles keypresses and automatically exits after command execution, preventing keyboard trapping.
- **5 Independent Timer Slots**: Pre-configured with graduated defaults (5, 10, 15, 25, and 60 minutes).
- **One-Time Quick Timer (`Q`)**: Dedicated in-memory countdown timer for custom ad-hoc durations without modifying persistent presets. Pressing `Q` when stopped opens the setup dialog directly on minutes and starts immediately upon pressing Enter.
- **Balanced Quad-Modifier Actions**:
  - `1` to `5`: Query current remaining time, or start countdown if stopped.
  - `Shift+1` to `Shift+5`: Pause or resume countdown.
  - `Control+1` to `Control+5`: Open duration configuration dialog (hours, minutes, seconds, and optional label).
  - `Alt+1` to `Alt+5`: Reset timer back to its initial configured duration.
- **Quick Timer Actions**:
  - `Q`: Query remaining quick timer (or open setup and start immediately if stopped).
  - `Shift+Q`: Pause running quick timer / Resume paused quick timer.
  - `Control+Q`: Open quick duration setup dialog and start immediately upon confirmation.
  - `Alt+Q`: Reset quick timer to stopped state and silence alarm.
- **In-Memory Stopwatch (`S`)**: Instant count-up stopwatch with `S` (start/query), `Shift+S` (pause/resume), `Control+S` (restart), and `Alt+S` (reset).
- **Auxiliary Layer Commands**:
  - `Space`: Immediately silence an active alarm audio.
  - `A`: Announce status summary for all 5 timer slots (and active quick timer).
  - `H`: Open command reference in NVDA browse mode.
  - `Escape`: Exit command layer silently.
- **Audio & Speech Notifications**:
  - Embedded wave alert (`alarm.wav`) on expiration (concise 1-second chime, automatically dismisses if not silenced).
  - Pre-emptive alarm handling: a newly expired timer immediately interrupts and replaces an older playing alarm.
  - Optional warning tone 10 seconds prior to expiration.
  - Flexible notification styles: Sound only, Speech only, or Sound and speech.
  - Dual verbosity modes: Beginner (descriptive instructions) and Advanced (concise numbers).
- **Session Persistence**: Configurable behavior on NVDA restart (resume active countdowns, keep paused, or reset to stopped).
- **Native Settings Panel**: Fully integrated into NVDA Settings dialog (`NVDA Menu -> Preferences -> Settings -> Tymer`).

---

## Command Reference

Activate the command layer by pressing **`NVDA+Y`**. A brief subtle tone confirms entry (if enabled in preferences). Then press any of the following keys:

| Key Combination | Action |
| :--- | :--- |
| `1` - `5` | Query remaining time (or start if stopped) |
| `Shift` + `1` - `5` | Pause running timer / Resume paused timer |
| `Control` + `1` - `5` | Open duration setup dialog |
| `Alt` + `1` - `5` | Reset timer to original duration |
| `Q` | Query remaining quick timer (or open setup and start if stopped) |
| `Shift` + `Q` | Pause running quick timer / Resume paused quick timer |
| `Control` + `Q` | Open quick duration setup dialog and start immediately |
| `Alt` + `Q` | Reset quick timer to stopped state and silence alarm |
| `S` | Query elapsed stopwatch time (or start if stopped) |
| `Shift` + `S` | Pause running stopwatch / Resume paused stopwatch |
| `Control` + `S` | Restart stopwatch immediately from zero |
| `Alt` + `S` | Reset stopwatch to zero and stop |
| `Space` | Silence sounding alarm |
| `A` | Report status of all timer slots |
| `H` | Open help window in browse mode |
| `Escape` | Cancel and exit layer |

*Note: Pressing an unassigned key inside the layer emits a low error tone and immediately releases keyboard control.*

---

## Configuration

To customize Tymer preferences, open **NVDA Menu -> Preferences -> Settings** and select **Tymer**:

1. **Expiry notification style**: Choose between *Sound only*, *Speech only*, or *Sound and speech*.
2. **Speech verbosity mode**: Choose *Beginner (descriptive)* for step-by-step modifier guidance, or *Advanced (concise)* for quick time readouts.
3. **Play audio cue when entering command layer**: Toggle the entry tone on `NVDA+Y`.
4. **Play warning cue 10 seconds before expiration**: Toggle a warning beep at 10 seconds remaining.
5. **Behavior on NVDA restart**: Select how ongoing timers behave across NVDA restarts (*Resume active countdowns*, *Reset all to stopped*, or *Keep countdowns paused*).
6. **Reset all timers to factory durations**: Restore all 5 slots to default durations (5, 10, 15, 25, 60 minutes) and clear custom labels.

---

## Compatibility

- Minimum NVDA Version: **2024.1**
- Last Tested NVDA Version: **2026.2**
- Operating System: Windows 10 / Windows 11

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version release notes and project history.

---

## Developer & Support

Developed by **Kamal Yaser** (كمال ياسر):

- **Email**: [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- **Telegram**: [@kamalyaser31](https://t.me/kamalyaser31)
- **Repository**: [https://github.com/kamalyaser31/tymer](https://github.com/kamalyaser31/tymer)

---

## License

Covered under the [GNU General Public License v2 (GPL-2.0)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
