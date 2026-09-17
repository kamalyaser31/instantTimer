# -*- coding: utf-8 -*-
# Tymer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

from typing import Callable, Optional
import wx
import gui
from gui.settingsDialogs import SettingsDialog
import config
import addonHandler
import ui
from .timerHandler import TimerSlot, CountdownEngine, formatTime

try:
    from logHandler import log
except ImportError:
    import logging

    log = logging.getLogger("tymer")

addonHandler.initTranslation()
_: Callable[[str], str]


class DurationDialog(SettingsDialog):
    """Accessible modal dialog to configure duration and optional label for a timer slot."""

    def __init__(
        self,
        parent: wx.Window,
        slot: TimerSlot,
        engine: Optional[CountdownEngine] = None,
    ):
        self.slot = slot
        self.engine = engine
        self._wasRunning = False

        if self.isQuick:
            self.title = _("Set Quick Timer Duration")
            if self.slot.state == "running":
                self._wasRunning = True
                self.slot.pause()
                if self.engine:
                    self.engine.notifySlotStateChanged()
        else:
            self.title = _("Set Timer {number} Duration").format(number=slot.index)

        super().__init__(parent)
        if self.isQuick:
            self.Bind(wx.EVT_CLOSE, self._onClose)

    @property
    def isQuick(self) -> bool:
        slot = getattr(self, "slot", None)
        return bool(slot and slot.index == 0)

    def makeSettings(self, settingsSizer: wx.Sizer) -> None:
        sizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        if not self.isQuick:
            self.labelEntry = sizerHelper.addLabeledControl(
                _("Timer &label (optional):"),
                wx.TextCtrl,
            )
            self.labelEntry.SetValue(self.slot.label)
        self._createTimeSpinCtrls(sizerHelper)

    def _createTimeSpinCtrls(self, sizerHelper: gui.guiHelper.BoxSizerHelper) -> None:
        totalSeconds = int(self.slot.duration)
        mins, secs = divmod(totalSeconds, 60)
        hrs, mins = divmod(mins, 60)
        self.hourEntry = sizerHelper.addLabeledControl(
            _("&Hours:"), wx.SpinCtrl, min=0, max=99, initial=min(hrs, 99)
        )
        self.minEntry = sizerHelper.addLabeledControl(
            _("&Minutes:"), wx.SpinCtrl, min=0, max=59, initial=min(mins, 59)
        )
        self.secEntry = sizerHelper.addLabeledControl(
            _("&Seconds:"), wx.SpinCtrl, min=0, max=59, initial=min(secs, 59)
        )

    def postInit(self) -> None:
        self.minEntry.SetFocus()

    def _resumeIfPaused(self) -> None:
        if getattr(self, "_wasRunning", False) and getattr(self, "slot", None):
            if self.slot.state == "paused":
                self._wasRunning = False
                self.slot.resume()
                if getattr(self, "engine", None):
                    self.engine.notifySlotStateChanged()

    def _parseDuration(self) -> int:
        hrs = self.hourEntry.GetValue()
        mins = self.minEntry.GetValue()
        secs = self.secEntry.GetValue()
        return hrs * 3600 + mins * 60 + secs

    def _startQuickTimer(self, totalSeconds: int) -> None:
        self.slot.setDuration(totalSeconds)
        self.slot.start()
        if getattr(self, "engine", None):
            self.engine.notifySlotStateChanged()
        ui.message(
            _("{name} started: {time}.").format(
                name=self.slot.displayName(), time=formatTime(self.slot.duration)
            )
        )

    def _saveSlotSettings(self, totalSeconds: int) -> None:
        newLabel = self.labelEntry.GetValue().strip()
        self.slot.setDuration(totalSeconds, newLabel)
        self._persistSlotSettings(self.slot.index, totalSeconds, newLabel)

    def onOk(self, evt: wx.CommandEvent) -> None:
        totalSeconds = self._parseDuration()
        if totalSeconds <= 0:
            gui.messageBox(
                _("Duration must be at least 1 second."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                self,
            )
            return

        self._wasRunning = False
        if self.isQuick:
            self._startQuickTimer(totalSeconds)
        else:
            self._saveSlotSettings(totalSeconds)
        super().onOk(evt)

    def onCancel(self, evt: wx.CommandEvent) -> None:
        self._resumeIfPaused()
        super().onCancel(evt)

    def _onClose(self, evt: wx.CloseEvent) -> None:
        self._resumeIfPaused()
        evt.Skip()

    def _persistSlotSettings(self, index: int, duration: int, label: str) -> None:
        try:
            durations = list(config.conf["tymer"]["defaultDurations"])
            labels = list(config.conf["tymer"]["slotLabels"])
            if 1 <= index <= len(durations):
                durations[index - 1] = duration
            if 1 <= index <= len(labels):
                labels[index - 1] = label
            config.conf["tymer"]["defaultDurations"] = durations
            config.conf["tymer"]["slotLabels"] = labels
            if config.conf["general"]["saveConfigurationOnExit"]:
                config.conf.save()
        except (KeyError, IndexError, TypeError):
            log.debugWarning("Tymer: Failed to persist slot settings", exc_info=True)


class QuickDurationDialog(DurationDialog):
    """Accessible modal dialog to quickly configure and start a one-time timer."""

    def __init__(self, parent: wx.Window, engine: CountdownEngine):
        super().__init__(parent, engine.quickSlot, engine=engine)
