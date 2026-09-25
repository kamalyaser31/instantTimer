# Instant Timer: countdown timers and stopwatch for NVDA

Instant Timer adds countdown timers and a stopwatch to the NVDA screen reader through a quick command layer (`NVDA+Y`). It includes five preset timers, an ad-hoc quick timer, and an in-memory stopwatch.

## Features

- **Modal command layer**: Press `NVDA+Y` to enter the layer. Pressing any layer key runs its action and immediately exits back to normal typing. Pressing an unassigned key beeps and exits.
- **Five preset timers**: Pre-set to 5, 10, 15, 25, and 60 minutes. Durations and optional labels can be adjusted at any time.
- **Quick timer (`Q`)**: An ad-hoc countdown timer that runs in memory without altering your five preset timers. Pressing `Q` when stopped opens the duration dialog focused on minutes; pressing Enter starts it immediately.
- **Stopwatch (`S`)**: An in-memory count-up timer.
- **Audible and spoken alerts**: Plays a 1-second wave chime on expiration and speaks the finished timer name. Includes an optional warning beep before expiration with configurable lead time.
- **Session persistence**: Can restore, pause, or reset active timers when NVDA restarts.
- **Settings panel**: Integrated directly into NVDA settings (`NVDA Menu > Preferences > Settings > Instant Timer`).

## Command reference

Press `NVDA+Y` to activate the layer. A short beep confirms entry if enabled in preferences. Then press one of the following keys:

| Key | Action |
| :--- | :--- |
| `1` to `5` | Check remaining time, or start if stopped |
| `Shift` + `1` to `5` | Reset timer to original duration |
| `Control` + `1` to `5` | Open duration and label dialog |
| `Alt` + `1` to `5` | Pause or resume timer |
| `Q` | Check quick timer (or open setup and start if stopped) |
| `Shift` + `Q` | Reset quick timer and silence alarm |
| `Control` + `Q` | Open quick timer duration dialog and start immediately |
| `Alt` + `Q` | Pause or resume quick timer |
| `S` | Check elapsed stopwatch time, or start if stopped |
| `Shift` + `S` | Reset stopwatch to zero and stop |
| `Control` + `S` | Restart stopwatch from zero |
| `Alt` + `S` | Pause or resume stopwatch |
| `Space` | Silence sounding alarm |
| `A` | Report status of all timers |
| `H` | Open help window in browse mode |
| `Escape` | Exit command layer |

Pressing an unassigned key plays a low error tone and releases keyboard control immediately.

## Configuration

Open **NVDA Menu > Preferences > Settings** and select **Instant Timer**:

1. **Expiry notification style**: Sound only, Speech only, or Sound and speech.
2. **Speech verbosity mode**: Beginner (descriptive guidance) or Advanced (concise numbers).
3. **Play audio cue when entering command layer**: Plays an entry tone on `NVDA+Y`.
4. **Play warning cue before expiration**: Plays a warning beep before a countdown reaches zero.
5. **Warning cue lead time in seconds**: The lead time before expiration (1 to 300 seconds, default: 10) when the warning sounds.
6. **Behavior on NVDA restart**: Resume active countdowns, reset all to stopped, or keep countdowns paused.
7. **Reset all timers to factory durations**: Resets all five timers to default durations (5, 10, 15, 25, 60 minutes) and clears custom labels.

## Compatibility

- Minimum NVDA version: 2024.1
- Last tested NVDA version: 2026.2
- Operating system: Windows 10 / Windows 11

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version release notes and project history.

## Developer and support

Developed by **Kamal Yaser** (كمال ياسر):

- Email: [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- Telegram: [@kamalyaser31](https://t.me/kamalyaser31)
- Repository: [https://github.com/kamalyaser31/instantTimer](https://github.com/kamalyaser31/instantTimer)

## License

Covered under the [GNU General Public License v2 (GPL-2.0)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
