# -*- coding: utf-8 -*-
# Instant Timer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

import time
from typing import Optional, List, Callable, Tuple, Any, Dict
import wx
import ui
import nvwave
import tones
import addonHandler
from . import paths

addonHandler.initTranslation()
_: Callable[[str], str]

DEFAULT_DURATIONS: List[int] = [300, 600, 900, 1500, 3600]
DEFAULT_SLOT_LABELS: List[str] = ["", "", "", "", ""]


def formatTime(seconds: float) -> str:
    """Formats a duration in seconds into a localized, human-friendly string."""
    totalSeconds = max(0, int(round(seconds)))
    if totalSeconds == 0:
        return _("0 seconds")
    minutes, secs = divmod(totalSeconds, 60)
    hours, minutes = divmod(minutes, 60)
    components: List[str] = []
    if hours == 1:
        components.append(_("1 hour"))
    elif hours > 1:
        components.append(_("{count} hours").format(count=hours))
    if minutes == 1:
        components.append(_("1 minute"))
    elif minutes > 1:
        components.append(_("{count} minutes").format(count=minutes))
    if secs == 1:
        components.append(_("1 second"))
    elif secs > 1:
        components.append(_("{count} seconds").format(count=secs))
    return ", ".join(components)


def formatDigitalTime(seconds: float) -> str:
    """Formats a duration into adaptive MM:SS or HH:MM:SS digital string."""
    totalSeconds = max(0, int(round(seconds)))
    minutes, secs = divmod(totalSeconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class Stopwatch:
    """Lightweight in-memory stopwatch counting upwards from zero."""

    def __init__(self):
        self.state = "stopped"
        self._startTime: Optional[float] = None
        self._accumulated: float = 0.0

    def start(self) -> None:
        self.state = "running"
        self._startTime = time.time()
        self._accumulated = 0.0
        tones.beep(440, 35)
        tones.beep(660, 35)

    def pause(self) -> None:
        if self.state == "running" and self._startTime is not None:
            self._accumulated += time.time() - self._startTime
            self._startTime = None
            self.state = "paused"
            tones.beep(400, 40)

    def resume(self) -> None:
        if self.state == "paused":
            self._startTime = time.time()
            self.state = "running"
            tones.beep(600, 40)

    def restart(self) -> None:
        self.start()

    def reset(self) -> None:
        self.state = "stopped"
        self._startTime = None
        self._accumulated = 0.0
        tones.beep(350, 30)
        tones.beep(250, 30)

    def elapsed(self) -> float:
        if self.state == "running" and self._startTime is not None:
            return self._accumulated + (time.time() - self._startTime)
        return self._accumulated

    def formatDigital(self) -> str:
        return formatDigitalTime(self.elapsed())


class TimerSlot:
    """Represents an individual countdown timer slot with discrete states."""

    def __init__(self, index: int, duration: float, label: str = ""):
        self.index = index
        self.duration = float(duration)
        self.label = label.strip()
        self.state = "stopped"
        self.targetTime: Optional[float] = None
        self.remainingOnPause: Optional[float] = None
        self.cueEmitted = False

    def displayName(self) -> str:
        """Returns the user label if defined, otherwise 'Timer N'."""
        if self.label:
            return self.label
        return _("Timer {index}").format(index=self.index)

    def start(self) -> None:
        """Starts countdown from initial duration."""
        self.state = "running"
        self.targetTime = time.time() + self.duration
        self.remainingOnPause = None
        self.cueEmitted = False

    def pause(self) -> None:
        """Pauses the running countdown and preserves remaining time."""
        if self.state == "running":
            self.remainingOnPause = self.remaining()
            self.state = "paused"
            self.targetTime = None

    def resume(self) -> None:
        """Resumes countdown from preserved remaining time."""
        if self.state == "paused":
            rem = (
                self.remainingOnPause
                if self.remainingOnPause is not None
                else self.duration
            )
            self.state = "running"
            self.targetTime = time.time() + rem
            self.remainingOnPause = None

    def reset(self) -> None:
        """Resets the timer back to its stopped initial state."""
        self.state = "stopped"
        self.targetTime = None
        self.remainingOnPause = None
        self.cueEmitted = False

    def setDuration(self, seconds: float, label: Optional[str] = None) -> None:
        """Sets new duration and optional label, then resets."""
        self.duration = max(1.0, float(seconds))
        if label is not None:
            self.label = label.strip()
        self.reset()

    def remaining(self) -> float:
        """Calculates remaining seconds towards zero."""
        if self.state == "running" and self.targetTime is not None:
            return max(0.0, self.targetTime - time.time())
        if self.state == "paused" and self.remainingOnPause is not None:
            return max(0.0, self.remainingOnPause)
        return self.duration


class CountdownEngine:
    """Coordinates all 5 timer slots, tick checks, alarm preemption, and reporting."""

    @staticmethod
    def _slotConfig(
        i: int, defaultDurations: List[int], defaultLabels: List[str]
    ) -> Tuple[int, str]:
        dur = defaultDurations[i] if i < len(defaultDurations) else (i + 1) * 300
        lbl = defaultLabels[i] if i < len(defaultLabels) else ""
        return dur, lbl

    def __init__(
        self,
        defaultDurations: Optional[List[int]] = None,
        defaultLabels: Optional[List[str]] = None,
        conf: Optional[Dict[str, Any]] = None,
    ):
        self.conf = conf if isinstance(conf, dict) else {}
        durations = (
            defaultDurations or self.conf.get("defaultDurations") or DEFAULT_DURATIONS
        )
        labels = defaultLabels or self.conf.get("slotLabels") or DEFAULT_SLOT_LABELS

        self.slots: List[TimerSlot] = []
        for i in range(5):
            dur, lbl = self._slotConfig(i, durations, labels)
            self.slots.append(TimerSlot(index=i + 1, duration=dur, label=lbl))

        self.quickSlot = TimerSlot(index=0, duration=300, label=_("Quick timer"))
        self._ticker = wx.PyTimer(self._onTick)
        self._alarmAutoStopTimer = wx.PyTimer(self.silenceAlarm)
        self.stopwatch = Stopwatch()
        self.isAlarmActive = False
        self._ensureTicker()

    def terminate(self) -> None:
        """Stops internal timers and silences audio."""
        self.silenceAlarm()
        if self._ticker.IsRunning():
            self._ticker.Stop()

    def _ensureTicker(self) -> None:
        """Runs ticker only when at least one countdown slot is actively running."""
        hasRunningSlot = any(
            slot.state == "running" for slot in self.slots + [self.quickSlot]
        )
        if hasRunningSlot and not self._ticker.IsRunning():
            self._ticker.Start(1000)
        elif not hasRunningSlot and self._ticker.IsRunning():
            self._ticker.Stop()

    def notifySlotStateChanged(self) -> None:
        """Notifies the engine that a slot transitioned state to adjust the ticker."""
        self._ensureTicker()

    def resetToDefaults(
        self,
        defaultDurations: Optional[List[int]] = None,
        defaultLabels: Optional[List[str]] = None,
    ) -> None:
        """Resets all slots to factory durations and labels in stopped state."""
        self.silenceAlarm()
        durations = defaultDurations or DEFAULT_DURATIONS
        labels = defaultLabels or DEFAULT_SLOT_LABELS
        for i, slot in enumerate(self.slots):
            dur, lbl = self._slotConfig(i, durations, labels)
            slot.setDuration(dur, lbl)
        self.quickSlot.reset()
        self._ensureTicker()

    def getSlot(self, index: int) -> Optional[TimerSlot]:
        """Safely retrieves a slot by 1-based index."""
        if 1 <= index <= len(self.slots):
            return self.slots[index - 1]
        return None

    def _onTick(self) -> None:
        """Periodic 1-second tick checking countdown expiries and cues."""
        for slot in self.slots + [self.quickSlot]:
            if slot.state != "running":
                continue
            rem = slot.remaining()
            cueSec = float(self._getPreExpirySeconds())
            if rem <= cueSec and not slot.cueEmitted:
                if self._isPreExpiryCueEnabled():
                    tones.beep(550, 40)
                slot.cueEmitted = True
            if rem <= 0.0:
                self.triggerAlarm(slot)
                slot.reset()
        self._ensureTicker()

    def _isPreExpiryCueEnabled(self) -> bool:
        return bool(self.conf.get("preExpiryCue", False))

    def _getPreExpirySeconds(self) -> int:
        try:
            return max(1, int(self.conf.get("preExpirySeconds", 10)))
        except (ValueError, TypeError):
            return 10

    def triggerAlarm(self, slot: TimerSlot) -> None:
        """Preempts ongoing alarms and announces expiry according to style."""
        self.silenceAlarm()
        self.isAlarmActive = True
        style = self._getNotificationStyle()
        # Style 0: Sound only, 1: Speech only, 2: Both
        if style in (0, 2):
            nvwave.playWaveFile(paths.ALARM_SOUND_PATH)
            self._alarmAutoStopTimer.StartOnce(1000)
        if style in (1, 2):
            msg = _("{name} expired: {duration}.").format(
                name=slot.displayName(),
                duration=formatTime(slot.duration),
            )
            ui.message(msg)

    def silenceAlarm(self) -> None:
        """Dismisses active alarm audio and stops auto-dismiss timer."""
        self.isAlarmActive = False
        if nvwave.fileWavePlayer is not None:
            nvwave.fileWavePlayer.stop()
        if self._alarmAutoStopTimer.IsRunning():
            self._alarmAutoStopTimer.Stop()

    def _getNotificationStyle(self) -> int:
        try:
            return int(self.conf.get("notificationStyle", 0))
        except (ValueError, TypeError):
            return 0

    def getStatusReport(self, slot: TimerSlot) -> str:
        """Generates localized speech output for a slot according to verbosity."""
        verbosity = self._getVerbosity()
        if verbosity == 1:
            return self._getConciseReport(slot)
        return self._getDescriptiveReport(slot)

    def _getVerbosity(self) -> int:
        try:
            return int(self.conf.get("verbosity", 0))
        except (ValueError, TypeError):
            return 0

    def _getConciseReport(self, slot: TimerSlot) -> str:
        name = slot.displayName()
        remStr = formatTime(slot.remaining())
        if slot.state == "running":
            return f"{name}: {remStr}"
        if slot.state == "paused":
            return _("{name}: paused, {time}").format(name=name, time=remStr)
        return _("{name}: stopped").format(name=name)

    def _getDescriptiveReport(self, slot: TimerSlot) -> str:
        name = slot.displayName()
        remStr = formatTime(slot.remaining())
        if slot.state == "running":
            return _("{name}: {time} remaining.").format(name=name, time=remStr)
        if slot.index == 0:
            if slot.state == "paused":
                return _("{name}: paused at {time}. Press Alt+Q to resume.").format(
                    name=name, time=remStr
                )
            return _("{name}: {duration}, stopped. Press Q to start.").format(
                name=name, duration=formatTime(slot.duration)
            )
        if slot.state == "paused":
            return _("{name}: paused at {time}. Press Alt+{index} to resume.").format(
                name=name, time=remStr, index=slot.index
            )
        return _("{name}: {duration}, stopped. Press {index} to start.").format(
            name=name, duration=formatTime(slot.duration), index=slot.index
        )

    def reportAllStatus(self) -> str:
        """Generates a combined summary of all timer slots and active quick timer."""
        reports: List[str] = []
        activeSlots = self.slots + (
            [self.quickSlot] if self.quickSlot.state != "stopped" else []
        )
        for slot in activeSlots:
            name = slot.displayName()
            if slot.state == "running":
                reports.append(f"{name}: {formatTime(slot.remaining())}")
            elif slot.state == "paused":
                reports.append(_("{name}: paused").format(name=name))
            else:
                reports.append(_("{name}: stopped").format(name=name))
        return "; ".join(reports)
