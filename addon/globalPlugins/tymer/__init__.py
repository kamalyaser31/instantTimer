# -*- coding: utf-8 -*-
# Tymer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

from typing import Callable, Tuple, List, Optional, Dict, Final
import time
import globalPluginHandler
import scriptHandler
import globalVars
import config
from configobj.validate import VdtTypeError
import gui
import ui
import tones
import addonHandler
from .timerHandler import (
    CountdownEngine,
    TimerSlot,
    formatTime,
    DEFAULT_DURATIONS,
    DEFAULT_SLOT_LABELS,
)
from .settingsGUI import TymerSettingsPanel
from .durationDialog import DurationDialog, QuickDurationDialog

addonHandler.initTranslation()
_: Callable[[str], str]

DEFAULT_CONFIG: Final = {
    "notificationStyle": 0,
    "verbosity": 0,
    "entryBeep": True,
    "preExpiryCue": False,
    "restartPolicy": "resume",
    "defaultDurations": DEFAULT_DURATIONS,
    "slotLabels": DEFAULT_SLOT_LABELS,
    "activeTimersData": ["", "", "", "", ""],
}

confspec = {
    "notificationStyle": "integer(default=0)",
    "verbosity": "integer(default=0)",
    "entryBeep": "boolean(default=True)",
    "preExpiryCue": "boolean(default=False)",
    "restartPolicy": "string(default='resume')",
    "defaultDurations": "int_list(default=list(300, 600, 900, 1500, 3600))",
    "slotLabels": "string_list(default=list('', '', '', '', ''))",
    "activeTimersData": "string_list(default=list('', '', '', '', ''))",
}
config.conf.spec["tymer"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """Global plugin managing the Tymer modal command layer and slots."""

    scriptCategory = _("Tymer")
    layerModeActive = False
    layeredScriptToRun: Optional[Callable] = None

    def __init__(self):
        super().__init__()
        if globalVars.appArgs.secure or config.isAppX:
            return

        self._validateConfiguration()
        gui.NVDASettingsDialog.categoryClasses.append(TymerSettingsPanel)

        conf = config.conf["tymer"]
        durations = [int(x) for x in conf["defaultDurations"]]
        labels = [str(x) for x in conf["slotLabels"]]
        self.engine = CountdownEngine(defaultDurations=durations, defaultLabels=labels)

        self._restoreSessionState()
        self._setupLayerGestures()

    def terminate(self):
        super().terminate()
        try:
            gui.NVDASettingsDialog.categoryClasses.remove(TymerSettingsPanel)
        except (ValueError, KeyError, AttributeError):
            pass
        if hasattr(self, "engine"):
            self._saveSessionState()
            self.engine.terminate()

    def _validateConfiguration(self):
        conf = config.conf["tymer"]
        validationFailed = False
        for key in (
            "notificationStyle",
            "verbosity",
            "entryBeep",
            "preExpiryCue",
            "restartPolicy",
        ):
            try:
                conf[key]
            except VdtTypeError:
                validationFailed = True
                conf.profiles[0][key] = DEFAULT_CONFIG[key]
        if validationFailed and config.conf["general"]["saveConfigurationOnExit"]:
            config.conf.save()

    def _restoreSessionState(self):
        policy = config.conf["tymer"].get("restartPolicy", "resume")
        if policy == "reset":
            return
        rawSaved = config.conf["tymer"].get("activeTimersData", [])
        now = time.time()
        for index, rawSlotData in enumerate(rawSaved):
            self._restoreSlotFromSaved(index, rawSlotData, policy, now)

    def _restoreSlotFromSaved(
        self, index: int, rawSlotData: str, policy: str, now: float
    ):
        if index >= len(self.engine.slots) or not rawSlotData:
            return
        try:
            state, rem = rawSlotData.split(":")
            remVal = float(rem)
            slot = self.engine.slots[index]
            if state == "running" and policy == "resume":
                slot.state = "running"
                slot.targetTime = now + remVal
                self.engine.notifySlotStateChanged()
            elif state in ("running", "paused"):
                slot.state = "paused"
                slot.remainingOnPause = remVal
        except (ValueError, IndexError):
            pass

    def _saveSessionState(self):
        activeData: List[str] = []
        for slot in self.engine.slots:
            if slot.state in ("running", "paused"):
                activeData.append(f"{slot.state}:{slot.remaining():.1f}")
            else:
                activeData.append("")
        config.conf["tymer"]["activeTimersData"] = activeData

    def _setupLayerGestures(self):
        self._layerGestures: List[Tuple[str, Callable, str]] = []
        self._gestureHandlers: Dict[str, Callable] = {}
        for i in range(1, 6):
            self._addSlotGestures(i)
        self._addQuickTimerGestures()
        self._addStopwatchGestures()
        self._addAuxiliaryGestures()

    def _registerSpecs(self, specs: List[Tuple[str, Callable, str]]):
        for key, handler, desc in specs:
            self._layerGestures.append((key, handler, desc))
            self._gestureHandlers[key] = handler

    def _addSlotGestures(self, index: int):
        self._registerSpecs(
            [
                (
                    str(index),
                    self._makeSlotQueryStart(index),
                    _("Query or start timer {0}").format(index),
                ),
                (
                    f"shift+{index}",
                    self._makeSlotReset(index),
                    _("Reset timer {0}").format(index),
                ),
                (
                    f"control+{index}",
                    self._makeSlotSetDuration(index),
                    _("Set duration for timer {0}").format(index),
                ),
                (
                    f"alt+{index}",
                    self._makeSlotPauseResume(index),
                    _("Pause or resume timer {0}").format(index),
                ),
            ]
        )

    def _addQuickTimerGestures(self):
        self._registerSpecs(
            [
                (
                    "q",
                    self._makeQuickTimerQueryOrStart(),
                    _("Query or set quick timer"),
                ),
                (
                    "shift+q",
                    self._makeQuickTimerReset(),
                    _("Reset quick timer"),
                ),
                (
                    "control+q",
                    self._makeQuickTimerSetDuration(),
                    _("Set duration for quick timer"),
                ),
                (
                    "alt+q",
                    self._makeQuickTimerPauseResume(),
                    _("Pause or resume quick timer"),
                ),
            ]
        )

    def _addStopwatchGestures(self):
        self._registerSpecs(
            [
                (
                    "s",
                    self._makeStopwatchQueryStart(),
                    _("Query or start stopwatch"),
                ),
                (
                    "shift+s",
                    self._makeStopwatchReset(),
                    _("Reset stopwatch to zero"),
                ),
                (
                    "control+s",
                    self._makeStopwatchRestart(),
                    _("Restart stopwatch from zero"),
                ),
                (
                    "alt+s",
                    self._makeStopwatchPauseResume(),
                    _("Pause or resume stopwatch"),
                ),
            ]
        )

    def _addAuxiliaryGestures(self):
        self._registerSpecs(
            [
                ("space", self.script_silenceAlarm, _("Silence active alarm")),
                ("a", self.script_reportAll, _("Report status of all timers")),
                ("h", self.script_help, _("Show command layer help in browse mode")),
                ("escape", self.script_cancelLayer, _("Exit command layer")),
            ]
        )

    def _openDurationDialog(self, slot: Optional[TimerSlot]) -> None:
        if not slot:
            return
        try:
            gui.mainFrame.prePopup()
            dialog = DurationDialog(gui.mainFrame, slot, engine=self.engine)
            dialog.Show()
            gui.mainFrame.postPopup()
        except gui.settingsDialogs.SettingsDialog.MultiInstanceErrorWithDialog:
            ui.message(_("Duration dialog is already open."))

    def _makePauseResumeHandler(
        self, slotGetter: Callable[[], Optional[TimerSlot]]
    ) -> Callable:
        def handler(gesture):
            slot = slotGetter()
            if not slot:
                return
            if slot.state == "running":
                slot.pause()
                self.engine.notifySlotStateChanged()
                ui.message(_("{name} paused.").format(name=slot.displayName()))
            elif slot.state == "paused":
                slot.resume()
                self.engine.notifySlotStateChanged()
                ui.message(_("{name} resumed.").format(name=slot.displayName()))
            else:
                ui.message(self.engine.getStatusReport(slot))

        return handler

    def _makeResetHandler(
        self, slotGetter: Callable[[], Optional[TimerSlot]]
    ) -> Callable:
        def handler(gesture):
            slot = slotGetter()
            if not slot:
                return
            slot.reset()
            self.engine.notifySlotStateChanged()
            self.engine.silenceAlarm()
            ui.message(
                _("{name} reset to {time}.").format(
                    name=slot.displayName(), time=formatTime(slot.duration)
                )
            )

        return handler

    def _makeSlotQueryStart(self, index: int) -> Callable:
        def handler(gesture):
            slot = self.engine.getSlot(index)
            if not slot:
                return
            if slot.state == "stopped":
                slot.start()
                self.engine.notifySlotStateChanged()
                ui.message(
                    _("{name} started: {time}.").format(
                        name=slot.displayName(), time=formatTime(slot.duration)
                    )
                )
            else:
                ui.message(self.engine.getStatusReport(slot))

        return handler

    def _makeSlotPauseResume(self, index: int) -> Callable:
        return self._makePauseResumeHandler(lambda: self.engine.getSlot(index))

    def _makeSlotSetDuration(self, index: int) -> Callable:
        return lambda gesture: self._openDurationDialog(self.engine.getSlot(index))

    def _makeSlotReset(self, index: int) -> Callable:
        return self._makeResetHandler(lambda: self.engine.getSlot(index))

    def _makeStopwatchQueryStart(self) -> Callable:
        def handler(gesture):
            sw = self.engine.stopwatch
            if sw.state == "stopped":
                sw.start()
                ui.message(_("Started"))
            elif sw.state == "running":
                ui.message(sw.formatDigital())
            elif sw.state == "paused":
                ui.message(_("{time}, paused").format(time=sw.formatDigital()))

        return handler

    def _makeStopwatchPauseResume(self) -> Callable:
        def handler(gesture):
            sw = self.engine.stopwatch
            if sw.state == "running":
                sw.pause()
                ui.message(_("Paused"))
            elif sw.state == "paused":
                sw.resume()
                ui.message(_("Resumed"))
            else:
                ui.message(_("Stopwatch is stopped."))

        return handler

    def _makeStopwatchRestart(self) -> Callable:
        def handler(gesture):
            self.engine.stopwatch.restart()
            ui.message(_("Restarted"))

        return handler

    def _makeStopwatchReset(self) -> Callable:
        def handler(gesture):
            self.engine.stopwatch.reset()
            ui.message(_("Reset"))

        return handler

    def _openQuickDurationDialog(self):
        self._openDurationDialog(self.engine.quickSlot)

    def _makeQuickTimerQueryOrStart(self) -> Callable:
        def handler(gesture):
            slot = self.engine.quickSlot
            if slot.state == "stopped":
                self._openDurationDialog(slot)
            else:
                ui.message(self.engine.getStatusReport(slot))

        return handler

    def _makeQuickTimerSetDuration(self) -> Callable:
        return lambda gesture: self._openDurationDialog(self.engine.quickSlot)

    def _makeQuickTimerPauseResume(self) -> Callable:
        return self._makePauseResumeHandler(lambda: self.engine.quickSlot)

    def _makeQuickTimerReset(self) -> Callable:
        return self._makeResetHandler(lambda: self.engine.quickSlot)

    @scriptHandler.script(
        category=scriptCategory,
        description=_(
            "Enters Tymer command layer. Press numbers 1-5 for timers, Q for quick timer, S for stopwatch, Space to silence, H for help."
        ),
        gesture="kb:NVDA+y",
    )
    def script_tymerLayerCommands(self, gesture):
        if self.layerModeActive:
            self.script_error(gesture)
            return

        for gestureSpec in self._layerGestures:
            self.bindGesture(f"kb:{gestureSpec[0]}", "layerAction")

        self.layerModeActive = True
        if config.conf["tymer"].get("entryBeep", True):
            tones.beep(100, 15)

    def script_layerAction(self, gesture):
        # Internal placeholder method bound to layer keys for NVDA script resolution
        pass

    def _getGestureKey(self, gesture) -> Optional[str]:
        rawIds = getattr(gesture, "identifiers", []) or [
            getattr(gesture, "identifier", "")
        ]
        for gid in rawIds:
            if not gid:
                continue
            normalized = gid.strip().lower()
            if normalized.startswith("kb("):
                idx = normalized.find("):")
                if idx != -1:
                    normalized = "kb:" + normalized[idx + 2 :]
            if normalized.startswith("kb:"):
                key = normalized[3:]
                if key in self._gestureHandlers:
                    return key
        return None

    def getScript(self, gesture):
        if not getattr(self, "layerModeActive", False):
            return super().getScript(gesture)
        script = super().getScript(gesture)
        if not script:
            return self.script_error
        key = self._getGestureKey(gesture)
        if key and key in self._gestureHandlers:
            self.layeredScriptToRun = self._gestureHandlers[key]
            return self.runAndFinish
        return self.script_error

    def runAndFinish(self, gesture):
        if self.layeredScriptToRun is not None:
            self.layeredScriptToRun(gesture)
        self.finish()

    def finish(self):
        self.layerModeActive = False
        self.clearGestureBindings()
        self.bindGesture("kb:NVDA+y", "tymerLayerCommands")

    def script_error(self, gesture):
        tones.beep(120, 100)
        self.finish()

    def script_silenceAlarm(self, gesture):
        self.engine.silenceAlarm()
        ui.message(_("Alarm silenced."))

    def script_reportAll(self, gesture):
        ui.message(self.engine.reportAllStatus())

    def script_cancelLayer(self, gesture):
        self.finish()

    def script_help(self, gesture):
        items = "".join(
            [
                f"<li><strong>{gestureSpec[0]}</strong>: {gestureSpec[2]}</li>"
                for gestureSpec in self._layerGestures
            ]
        )
        html = f"<h1>{_('Tymer Layer Commands')}</h1><ul>{items}</ul>"
        ui.browseableMessage(html, _("Tymer Help"), isHtml=True)
