# -*- coding: utf-8 -*-
# Tymer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

from typing import Callable, Tuple, List
import wx
import gui
from gui.settingsDialogs import SettingsPanel
import config
import addonHandler

addonHandler.initTranslation()
_: Callable[[str], str]


class TymerSettingsPanel(SettingsPanel):
    """Preferences settings panel for Tymer integrated into NVDA Settings."""

    title = _("Tymer")

    _notificationChoices: Tuple[str, ...] = (
        _("Sound only"),
        _("Speech only"),
        _("Sound and speech"),
    )

    _verbosityChoices: Tuple[str, ...] = (
        _("Beginner (descriptive)"),
        _("Advanced (concise)"),
    )

    _restartPolicyChoices: Tuple[str, ...] = (
        _("Resume active countdowns"),
        _("Reset all to stopped"),
        _("Keep countdowns paused"),
    )

    _restartPolicyKeys: Tuple[str, ...] = ("resume", "reset", "pause")

    def makeSettings(self, settingsSizer: wx.Sizer) -> None:
        sizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        self._createControls(sizerHelper)
        self._loadCurrentValues()

    def _createControls(self, sizerHelper: gui.guiHelper.BoxSizerHelper) -> None:
        self.notificationStyleChoice = sizerHelper.addLabeledControl(
            _("Expiry notification &style:"),
            wx.Choice,
            choices=self._notificationChoices,
        )
        self.verbosityChoice = sizerHelper.addLabeledControl(
            _("Speech &verbosity mode:"),
            wx.Choice,
            choices=self._verbosityChoices,
        )
        self.entryBeepCheckBox = sizerHelper.addItem(
            wx.CheckBox(self, label=_("&Play audio cue when entering command layer")),
        )
        self.preExpiryCueCheckBox = sizerHelper.addItem(
            wx.CheckBox(self, label=_("Play &warning cue before expiration")),
        )
        self.preExpiryCueCheckBox.Bind(wx.EVT_CHECKBOX, self._onTogglePreExpiryCue)
        self.preExpirySecondsSpinCtrl = sizerHelper.addLabeledControl(
            _("Warning cue &lead time in seconds:"),
            wx.SpinCtrl,
            min=1,
            max=300,
            initial=10,
        )
        self.restartPolicyChoice = sizerHelper.addLabeledControl(
            _("Behavior on NVDA &restart:"),
            wx.Choice,
            choices=self._restartPolicyChoices,
        )
        self.resetDefaultsButton = sizerHelper.addItem(
            wx.Button(self, label=_("Reset all timers to &factory durations")),
        )
        self.resetDefaultsButton.Bind(wx.EVT_BUTTON, self.onResetDefaults)

    def _onTogglePreExpiryCue(self, evt: wx.CommandEvent) -> None:
        self.preExpirySecondsSpinCtrl.Enable(self.preExpiryCueCheckBox.GetValue())

    @staticmethod
    def _safeIndex(val: object, maxLen: int) -> int:
        try:
            idx = int(val)
            return idx if 0 <= idx < maxLen else 0
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _safeClamp(val: object, minVal: int, maxVal: int, default: int) -> int:
        try:
            intVal = int(val)
            return max(minVal, min(maxVal, intVal))
        except (ValueError, TypeError):
            return default

    def _loadCurrentValues(self) -> None:
        conf = config.conf["tymer"]
        self.notificationStyleChoice.SetSelection(
            self._safeIndex(
                conf.get("notificationStyle", 0), len(self._notificationChoices)
            )
        )
        self.verbosityChoice.SetSelection(
            self._safeIndex(conf.get("verbosity", 0), len(self._verbosityChoices))
        )

        self.entryBeepCheckBox.SetValue(bool(conf.get("entryBeep", True)))
        cueEnabled = bool(conf.get("preExpiryCue", False))
        self.preExpiryCueCheckBox.SetValue(cueEnabled)
        cueSeconds = self._safeClamp(conf.get("preExpirySeconds", 10), 1, 300, 10)
        self.preExpirySecondsSpinCtrl.SetValue(cueSeconds)
        self.preExpirySecondsSpinCtrl.Enable(cueEnabled)

        policy = str(conf.get("restartPolicy", "resume"))
        if policy in self._restartPolicyKeys:
            self.restartPolicyChoice.SetSelection(self._restartPolicyKeys.index(policy))
        else:
            self.restartPolicyChoice.SetSelection(0)

    def onResetDefaults(self, evt: wx.CommandEvent) -> None:
        if (
            gui.messageBox(
                _(
                    "Are you sure you want to reset all timer durations to factory defaults?"
                ),
                _("Confirm Reset"),
                wx.YES_NO | wx.ICON_QUESTION,
                self,
            )
            == wx.YES
        ):
            from .timerHandler import DEFAULT_DURATIONS, DEFAULT_SLOT_LABELS

            durations = list(DEFAULT_DURATIONS)
            labels = list(DEFAULT_SLOT_LABELS)
            config.conf["tymer"]["defaultDurations"] = durations
            config.conf["tymer"]["slotLabels"] = labels
            self._syncRunningEngine(durations, labels)
            gui.messageBox(
                _("Timer durations reset to factory defaults."),
                _("Reset Complete"),
                wx.OK | wx.ICON_INFORMATION,
                self,
            )

    def _syncRunningEngine(self, durations: List[int], labels: List[str]) -> None:
        try:
            import globalPluginHandler

            for plugin in getattr(globalPluginHandler, "runningPlugins", []):
                if plugin.__class__.__name__ == "GlobalPlugin" and hasattr(
                    plugin, "engine"
                ):
                    plugin.engine.resetToDefaults(durations, labels)
                    break
        except Exception:
            pass

    def onSave(self) -> None:
        conf = config.conf["tymer"]
        conf["notificationStyle"] = self.notificationStyleChoice.GetSelection()
        conf["verbosity"] = self.verbosityChoice.GetSelection()
        conf["entryBeep"] = self.entryBeepCheckBox.GetValue()
        conf["preExpiryCue"] = self.preExpiryCueCheckBox.GetValue()
        conf["preExpirySeconds"] = self.preExpirySecondsSpinCtrl.GetValue()
        selectedPolicyIndex = self.restartPolicyChoice.GetSelection()
        conf["restartPolicy"] = self._restartPolicyKeys[selectedPolicyIndex]
