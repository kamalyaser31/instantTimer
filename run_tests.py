# -*- coding: utf-8 -*-
"""Standalone test runner for Tymer NVDA add-on.

Tests core logic, timing calculations, slot state transitions,
formatting, gesture normalization, and build metadata.
Adheres strictly to test-guard principles: behavior testing,
data-driven variants, and scenario-based naming.
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock

# Set up mocks for NVDA runtime modules before importing plugin modules
mock_addonHandler = MagicMock()
mock_addonHandler.initTranslation = MagicMock()
mock_addonHandler.getCodeAddon.return_value.path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "addon")
)


class MockProfileDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiles = [self]


class MockConf(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec = {}
        self.profiles = [self]
        self.save = MagicMock()


mock_config = MagicMock()
mock_config.conf = MockConf(
    {
        "tymer": MockProfileDict(
            {
                "notificationStyle": 0,
                "verbosity": 0,
                "entryBeep": True,
                "preExpiryCue": False,
                "restartPolicy": "resume",
                "defaultDurations": [300, 600, 900, 1500, 3600],
                "slotLabels": ["", "", "", "", ""],
                "activeTimersData": ["", "", "", "", ""],
            }
        ),
        "general": {"saveConfigurationOnExit": False},
    }
)

mock_nvwave = MagicMock()
mock_nvwave.fileWavePlayer = None
mock_nvwave.playWaveFile = MagicMock()

mock_tones = MagicMock()
mock_tones.beep = MagicMock()

mock_ui = MagicMock()
mock_ui.message = MagicMock()
mock_ui.browseableMessage = MagicMock()

mock_wx = MagicMock()


class MockPyTimer:
    def __init__(self, callback):
        self.callback = callback
        self._running = False

    def Start(self, millis):
        self._running = True

    def StartOnce(self, millis):
        self._running = True

    def Stop(self):
        self._running = False

    def IsRunning(self):
        return self._running


mock_wx.PyTimer = MockPyTimer
mock_wx.Window = object

mock_gui = MagicMock()
mock_globalPluginHandler = MagicMock()
mock_globalPluginHandler.GlobalPlugin = object
mock_scriptHandler = MagicMock()
mock_scriptHandler.script = lambda **kwargs: (lambda fn: fn)
mock_globalVars = MagicMock()
mock_globalVars.appArgs.secure = False

sys.modules["addonHandler"] = mock_addonHandler
sys.modules["config"] = mock_config
sys.modules["nvwave"] = mock_nvwave
sys.modules["tones"] = mock_tones
sys.modules["ui"] = mock_ui
sys.modules["wx"] = mock_wx
sys.modules["gui"] = mock_gui


class MockSettingsDialog:
    def __init__(self, parent):
        self.parent = parent

    def Bind(self, *args, **kwargs):
        pass

    def onOk(self, evt):
        pass

    def onCancel(self, evt):
        pass


mock_settings_dialogs = MagicMock()
mock_settings_dialogs.SettingsPanel = object
mock_settings_dialogs.SettingsDialog = MockSettingsDialog
mock_gui.settingsDialogs = mock_settings_dialogs
sys.modules["gui.settingsDialogs"] = mock_settings_dialogs
sys.modules["globalPluginHandler"] = mock_globalPluginHandler
sys.modules["scriptHandler"] = mock_scriptHandler
sys.modules["globalVars"] = mock_globalVars


class VdtTypeError(TypeError):
    pass


mock_validate = MagicMock()
mock_validate.VdtTypeError = VdtTypeError
sys.modules["configobj.validate"] = mock_validate

# Inject dummy translation function _ into builtins
import builtins

builtins._ = lambda s: s

# Add plugin path to sys.path
addon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "addon"))
plugin_dir = os.path.join(addon_path, "globalPlugins", "tymer")
sys.path.insert(0, os.path.join(addon_path, "globalPlugins"))

from tymer.timerHandler import (
    TimerSlot,
    CountdownEngine,
    formatTime,
    Stopwatch,
    formatDigitalTime,
)
from tymer import paths, GlobalPlugin, timerHandler
from tymer.durationDialog import QuickDurationDialog
import buildVars


class DummyGesture:
    """Lightweight test gesture representing keyboard identifiers from NVDA."""

    def __init__(self, identifier: str):
        self.identifiers = [identifier]
        self.identifier = identifier


class TestFormatTimeBehavior(unittest.TestCase):
    """Rule 3: One scenario per test, data-driven for variants."""

    def test_duration_formats_to_localized_human_units(self):
        cases = [
            (0, "0 seconds"),
            (-5, "0 seconds"),
            (1, "1 second"),
            (45, "45 seconds"),
            (60, "1 minute"),
            (120, "2 minutes"),
            (125, "2 minutes, 5 seconds"),
            (300, "5 minutes"),
            (3600, "1 hour"),
            (3665, "1 hour, 1 minute, 5 seconds"),
            (7200, "2 hours"),
            (7325, "2 hours, 2 minutes, 5 seconds"),
        ]
        for seconds, expected in cases:
            with self.subTest(seconds=seconds, expected=expected):
                self.assertEqual(formatTime(seconds), expected)


class TestTimerSlotLifecycle(unittest.TestCase):
    """Verifies state machine transitions and duration updates on real TimerSlot instances."""

    def setUp(self):
        self.slot = TimerSlot(index=1, duration=300, label="Work")

    def test_slot_initializes_in_stopped_state_with_given_metadata(self):
        self.assertEqual(self.slot.index, 1)
        self.assertEqual(self.slot.duration, 300.0)
        self.assertEqual(self.slot.label, "Work")
        self.assertEqual(self.slot.state, "stopped")
        self.assertIsNone(self.slot.targetTime)
        self.assertIsNone(self.slot.remainingOnPause)
        self.assertFalse(self.slot.cueEmitted)
        self.assertEqual(self.slot.displayName(), "Work")

    def test_slot_without_custom_label_falls_back_to_canonical_number(self):
        slot = TimerSlot(index=3, duration=600, label="")
        self.assertEqual(slot.displayName(), "Timer 3")

    def test_start_transitions_to_running_and_sets_future_target_time(self):
        self.slot.start()
        self.assertEqual(self.slot.state, "running")
        self.assertIsNotNone(self.slot.targetTime)
        self.assertAlmostEqual(self.slot.remaining(), 300.0, delta=1.0)

    def test_pause_and_resume_preserves_remaining_duration_across_states(self):
        self.slot.start()
        self.slot.pause()
        self.assertEqual(self.slot.state, "paused")
        self.assertIsNone(self.slot.targetTime)
        self.assertIsNotNone(self.slot.remainingOnPause)
        paused_rem = self.slot.remaining()
        self.assertAlmostEqual(paused_rem, 300.0, delta=1.0)

        self.slot.resume()
        self.assertEqual(self.slot.state, "running")
        self.assertIsNotNone(self.slot.targetTime)
        self.assertIsNone(self.slot.remainingOnPause)

    def test_reset_returns_running_slot_to_stopped_initial_state(self):
        self.slot.start()
        self.slot.cueEmitted = True
        self.slot.reset()
        self.assertEqual(self.slot.state, "stopped")
        self.assertIsNone(self.slot.targetTime)
        self.assertIsNone(self.slot.remainingOnPause)
        self.assertFalse(self.slot.cueEmitted)
        self.assertEqual(self.slot.remaining(), 300.0)

    def test_set_duration_updates_time_and_resets_active_countdown(self):
        self.slot.start()
        self.slot.setDuration(900, "Deep Work")
        self.assertEqual(self.slot.duration, 900.0)
        self.assertEqual(self.slot.label, "Deep Work")
        self.assertEqual(self.slot.state, "stopped")
        self.assertEqual(self.slot.remaining(), 900.0)


class TestCountdownEngineBehavior(unittest.TestCase):
    """Verifies multi-slot coordination, ticks, cues, and reporting."""

    def setUp(self):
        durations = [300, 600, 900, 1500, 3600]
        labels = ["Slot1", "", "", "", ""]
        self.engine = CountdownEngine(defaultDurations=durations, defaultLabels=labels)

    def tearDown(self):
        self.engine.terminate()

    def test_engine_initializes_exactly_five_configured_slots(self):
        self.assertEqual(len(self.engine.slots), 5)
        self.assertEqual(self.engine.slots[0].duration, 300)
        self.assertEqual(self.engine.slots[4].duration, 3600)
        self.assertEqual(self.engine.slots[0].label, "Slot1")
        self.assertEqual(self.engine.slots[1].label, "")

    def test_get_slot_returns_valid_slot_or_none_for_out_of_bounds(self):
        self.assertIsNotNone(self.engine.getSlot(1))
        self.assertIsNotNone(self.engine.getSlot(5))
        self.assertIsNone(self.engine.getSlot(0))
        self.assertIsNone(self.engine.getSlot(6))

    def test_tick_triggers_alarm_and_auto_resets_slot_when_target_time_lapses(self):
        slot = self.engine.slots[0]
        slot.start()
        slot.targetTime = time.time() - 1.0
        self.engine._onTick()
        self.assertEqual(slot.state, "stopped")
        self.assertEqual(slot.remaining(), 300.0)
        self.assertIsNone(slot.targetTime)
        self.assertTrue(self.engine.isAlarmActive)

    def test_tick_emits_warning_cue_at_ten_seconds_when_enabled(self):
        mock_tones.beep.reset_mock()
        mock_config.conf["tymer"]["preExpiryCue"] = True
        slot = self.engine.slots[1]
        slot.start()
        slot.targetTime = time.time() + 8.0
        self.engine._onTick()
        self.assertTrue(slot.cueEmitted)
        mock_tones.beep.assert_called_with(550, 40)

    def test_status_reports_switch_between_beginner_and_advanced_formats(self):
        slot = self.engine.slots[0]
        mock_config.conf["tymer"]["verbosity"] = 0
        rep_beg = self.engine.getStatusReport(slot)
        self.assertIn("stopped", rep_beg)

        mock_config.conf["tymer"]["verbosity"] = 1
        rep_adv = self.engine.getStatusReport(slot)
        self.assertIn("stopped", rep_adv)

    def test_report_all_status_aggregates_all_five_slots_into_summary(self):
        summary = self.engine.reportAllStatus()
        self.assertIn("Slot1: stopped", summary)
        self.assertIn("Timer 2: stopped", summary)

    def test_ticker_only_runs_when_slot_is_actively_running(self):
        self.assertFalse(self.engine._ticker.IsRunning())
        slot = self.engine.slots[0]
        slot.start()
        self.engine.notifySlotStateChanged()
        self.assertTrue(self.engine._ticker.IsRunning())
        slot.pause()
        self.engine.notifySlotStateChanged()
        self.assertFalse(self.engine._ticker.IsRunning())
        slot.resume()
        self.engine.notifySlotStateChanged()
        self.assertTrue(self.engine._ticker.IsRunning())
        slot.reset()
        self.engine.notifySlotStateChanged()
        self.assertFalse(self.engine._ticker.IsRunning())

    def test_reset_to_defaults_updates_all_slots_and_silences_alarms(self):
        self.engine.slots[0].setDuration(1234, "Custom")
        self.engine.isAlarmActive = True
        self.engine.resetToDefaults([300, 600, 900, 1500, 3600], ["", "", "", "", ""])
        self.assertEqual(self.engine.slots[0].duration, 300.0)
        self.assertEqual(self.engine.slots[0].label, "")
        self.assertFalse(self.engine.isAlarmActive)
        self.assertFalse(self.engine._ticker.IsRunning())


class TestPluginGestureResolution(unittest.TestCase):
    """Rule 1 & Rule 2: Tests REAL GlobalPlugin._getGestureKey resolution against genuine mapping."""

    def setUp(self):
        self.plugin = GlobalPlugin.__new__(GlobalPlugin)
        self.plugin.engine = CountdownEngine(
            defaultDurations=[300, 600, 900, 1500, 3600],
            defaultLabels=["", "", "", "", ""],
        )
        self.plugin._setupLayerGestures()

    def tearDown(self):
        self.plugin.engine.terminate()

    def test_get_gesture_key_normalizes_desktop_and_laptop_identifiers(self):
        cases = [
            ("kb:1", "1"),
            ("kb(desktop):1", "1"),
            ("kb(laptop):1", "1"),
            ("kb:shift+1", "shift+1"),
            ("kb(laptop):shift+1", "shift+1"),
            ("kb:control+2", "control+2"),
            ("kb:alt+3", "alt+3"),
            ("kb:s", "s"),
            ("kb:shift+s", "shift+s"),
            ("kb:control+s", "control+s"),
            ("kb:alt+s", "alt+s"),
            ("kb:q", "q"),
            ("kb(desktop):q", "q"),
            ("kb(laptop):shift+q", "shift+q"),
            ("kb:control+q", "control+q"),
            ("kb:alt+q", "alt+q"),
            ("kb:space", "space"),
            ("kb:a", "a"),
            ("kb:h", "h"),
            ("kb:escape", "escape"),
            ("kb:z", None),
            ("kb:f1", None),
            ("kb:enter", None),
        ]
        for raw_id, expected_key in cases:
            with self.subTest(raw_id=raw_id, expected_key=expected_key):
                gesture = DummyGesture(raw_id)
                resolved = self.plugin._getGestureKey(gesture)
                self.assertEqual(resolved, expected_key)


class TestPluginLayerLifecycle(unittest.TestCase):
    """Verifies that layer exit safely releases bindings and restores master hotkey."""

    def test_finish_releases_layer_mode_and_rebinds_layer_trigger(self):
        plugin = GlobalPlugin.__new__(GlobalPlugin)
        plugin.layerModeActive = True
        plugin.clearGestureBindings = MagicMock()
        plugin.bindGesture = MagicMock()

        plugin.finish()

        self.assertFalse(plugin.layerModeActive)
        plugin.clearGestureBindings.assert_called_once()
        plugin.bindGesture.assert_called_once_with("kb:NVDA+y", "tymerLayerCommands")


class TestPluginConfigurationAndSession(unittest.TestCase):
    """Verifies configuration validation fallback, session persistence, and alarm silencing on reset."""

    def setUp(self):
        self.plugin = GlobalPlugin.__new__(GlobalPlugin)
        self.plugin.engine = CountdownEngine(
            defaultDurations=[300, 600, 900, 1500, 3600],
            defaultLabels=["", "", "", "", ""],
        )

    def tearDown(self):
        self.plugin.engine.terminate()

    def test_validate_configuration_recovers_with_actual_defaults_on_vdt_error(self):
        from tymer import DEFAULT_CONFIG

        class CorruptConf(MockProfileDict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.error_triggered = False

            def __getitem__(self, item):
                if item == "notificationStyle" and not self.error_triggered:
                    self.error_triggered = True
                    raise VdtTypeError("corrupt")
                return super().__getitem__(item)

        corrupt = CorruptConf(
            {
                "notificationStyle": "invalid",
                "verbosity": 0,
                "entryBeep": True,
                "preExpiryCue": False,
                "restartPolicy": "resume",
            }
        )
        mock_config.conf["tymer"] = corrupt
        self.plugin._validateConfiguration()
        self.assertEqual(
            corrupt["notificationStyle"], DEFAULT_CONFIG["notificationStyle"]
        )

    def test_restore_session_state_with_resume_and_pause_policies(self):
        now = time.time()
        self.plugin._restoreSlotFromSaved(0, "running:150.0", "resume", now)
        slot0 = self.plugin.engine.slots[0]
        self.assertEqual(slot0.state, "running")
        self.assertAlmostEqual(slot0.remaining(), 150.0, delta=1.0)

        self.plugin._restoreSlotFromSaved(1, "running:200.0", "pause", now)
        slot1 = self.plugin.engine.slots[1]
        self.assertEqual(slot1.state, "paused")
        self.assertEqual(slot1.remainingOnPause, 200.0)

    def test_reset_slot_silences_active_alarm(self):
        slot = self.plugin.engine.slots[0]
        self.plugin.engine.isAlarmActive = True
        self.plugin.engine.silenceAlarm = MagicMock()

        handler = self.plugin._makeSlotReset(1)
        handler(None)

        self.assertEqual(slot.state, "stopped")
        self.plugin.engine.silenceAlarm.assert_called_once()


class TestStopwatchBehavior(unittest.TestCase):
    """Verifies in-memory count-up stopwatch transitions, timing, and formatting."""

    def setUp(self):
        self.sw = timerHandler.Stopwatch()

    def test_stopwatch_initializes_in_stopped_zero_state(self):
        self.assertEqual(self.sw.state, "stopped")
        self.assertEqual(self.sw.elapsed(), 0.0)
        self.assertEqual(self.sw.formatDigital(), "00:00")

    def test_start_transitions_to_running_and_advances_elapsed(self):
        self.sw.start()
        self.assertEqual(self.sw.state, "running")
        time.sleep(0.01)
        self.assertGreater(self.sw.elapsed(), 0.0)

    def test_pause_freezes_elapsed_time(self):
        self.sw.start()
        time.sleep(0.02)
        self.sw.pause()
        self.assertEqual(self.sw.state, "paused")
        frozen = self.sw.elapsed()
        time.sleep(0.02)
        self.assertEqual(self.sw.elapsed(), frozen)

    def test_resume_continues_accumulating_from_pause(self):
        self.sw.start()
        time.sleep(0.01)
        self.sw.pause()
        frozen = self.sw.elapsed()
        self.sw.resume()
        self.assertEqual(self.sw.state, "running")
        time.sleep(0.01)
        self.assertGreater(self.sw.elapsed(), frozen)

    def test_restart_resets_elapsed_to_zero_and_keeps_running(self):
        self.sw.start()
        time.sleep(0.02)
        self.sw.restart()
        self.assertEqual(self.sw.state, "running")
        self.assertLess(self.sw.elapsed(), 0.02)

    def test_reset_returns_stopwatch_to_stopped_zero_state(self):
        self.sw.start()
        time.sleep(0.01)
        self.sw.reset()
        self.assertEqual(self.sw.state, "stopped")
        self.assertEqual(self.sw.elapsed(), 0.0)

    def test_format_digital_time_variants(self):
        cases = [
            (0, "00:00"),
            (5, "00:05"),
            (65, "01:05"),
            (3599, "59:59"),
            (3600, "01:00:00"),
            (3665, "01:01:05"),
        ]
        for secs, expected in cases:
            with self.subTest(secs=secs, expected=expected):
                self.assertEqual(timerHandler.formatDigitalTime(secs), expected)


class TestQuickTimerBehavior(unittest.TestCase):
    """Verifies dedicated in-memory quick timer slot, ticker adjustments, and dialog lifecycle."""

    def setUp(self):
        self.engine = CountdownEngine(
            defaultDurations=[300, 600, 900, 1500, 3600],
            defaultLabels=["", "", "", "", ""],
        )

    def tearDown(self):
        self.engine.terminate()

    def test_quick_slot_initializes_with_correct_defaults(self):
        qs = self.engine.quickSlot
        self.assertEqual(qs.index, 0)
        self.assertEqual(qs.duration, 300.0)
        self.assertEqual(qs.state, "stopped")
        self.assertEqual(qs.displayName(), "Quick timer")

    def test_quick_slot_ticker_activation(self):
        qs = self.engine.quickSlot
        self.assertFalse(self.engine._ticker.IsRunning())
        qs.start()
        self.engine.notifySlotStateChanged()
        self.assertTrue(self.engine._ticker.IsRunning())
        qs.pause()
        self.engine.notifySlotStateChanged()
        self.assertFalse(self.engine._ticker.IsRunning())
        qs.resume()
        self.engine.notifySlotStateChanged()
        self.assertTrue(self.engine._ticker.IsRunning())
        qs.reset()
        self.engine.notifySlotStateChanged()
        self.assertFalse(self.engine._ticker.IsRunning())

    def test_quick_slot_tick_triggers_alarm_and_autoresets(self):
        qs = self.engine.quickSlot
        qs.start()
        qs.targetTime = time.time() - 1.0
        self.engine.triggerAlarm = MagicMock()
        self.engine._onTick()
        self.engine.triggerAlarm.assert_called_once_with(qs)
        self.assertEqual(qs.state, "stopped")
        self.assertIsNone(qs.targetTime)

    def test_quick_slot_in_report_all_status(self):
        rep_stopped = self.engine.reportAllStatus()
        self.assertNotIn("Quick timer", rep_stopped)

        self.engine.quickSlot.start()
        rep_running = self.engine.reportAllStatus()
        self.assertIn("Quick timer:", rep_running)

        self.engine.quickSlot.pause()
        rep_paused = self.engine.reportAllStatus()
        self.assertIn("Quick timer: paused", rep_paused)

    def test_quick_slot_descriptive_report_instructions(self):
        qs = self.engine.quickSlot
        desc_stopped = self.engine._getDescriptiveReport(qs)
        self.assertIn("Press Q to start", desc_stopped)

        qs.start()
        qs.pause()
        desc_paused = self.engine._getDescriptiveReport(qs)
        self.assertIn("Press Shift+Q to resume", desc_paused)

    def test_quick_duration_dialog_ok_starts_countdown(self):
        dialog = QuickDurationDialog.__new__(QuickDurationDialog)
        dialog.engine = self.engine
        dialog.slot = self.engine.quickSlot
        dialog._wasRunning = False
        dialog.hourEntry = MagicMock(GetValue=lambda: 0)
        dialog.minEntry = MagicMock(GetValue=lambda: 7)
        dialog.secEntry = MagicMock(GetValue=lambda: 30)

        mock_evt = MagicMock()
        dialog.onOk(mock_evt)

        self.assertEqual(self.engine.quickSlot.duration, 450.0)
        self.assertEqual(self.engine.quickSlot.state, "running")
        self.assertFalse(dialog._wasRunning)

    def test_quick_duration_dialog_rejects_zero_duration(self):
        dialog = QuickDurationDialog.__new__(QuickDurationDialog)
        dialog.engine = self.engine
        dialog.slot = self.engine.quickSlot
        dialog.slot.duration = 300.0
        dialog._wasRunning = False
        dialog.hourEntry = MagicMock(GetValue=lambda: 0)
        dialog.minEntry = MagicMock(GetValue=lambda: 0)
        dialog.secEntry = MagicMock(GetValue=lambda: 0)

        mock_evt = MagicMock()
        dialog.onOk(mock_evt)

        self.assertEqual(self.engine.quickSlot.duration, 300.0)
        self.assertEqual(self.engine.quickSlot.state, "stopped")

    def test_quick_duration_dialog_pauses_running_and_resumes_on_cancel(self):
        self.engine.quickSlot.start()
        self.assertEqual(self.engine.quickSlot.state, "running")

        dialog = QuickDurationDialog.__new__(QuickDurationDialog)
        dialog.engine = self.engine
        dialog.slot = self.engine.quickSlot
        dialog._wasRunning = self.engine.quickSlot.state == "running"
        if dialog._wasRunning:
            dialog.slot.pause()
            dialog.engine.notifySlotStateChanged()

        self.assertEqual(self.engine.quickSlot.state, "paused")

        dialog.onCancel(MagicMock())
        self.assertEqual(self.engine.quickSlot.state, "running")

    def test_quick_timer_plugin_layer_handlers(self):
        plugin = GlobalPlugin.__new__(GlobalPlugin)
        plugin.engine = self.engine
        plugin._setupLayerGestures()

        pause_resume = plugin._makeQuickTimerPauseResume()
        self.engine.quickSlot.start()
        pause_resume(None)
        self.assertEqual(self.engine.quickSlot.state, "paused")
        pause_resume(None)
        self.assertEqual(self.engine.quickSlot.state, "running")

        reset_handler = plugin._makeQuickTimerReset()
        self.engine.isAlarmActive = True
        self.engine.silenceAlarm = MagicMock()
        reset_handler(None)
        self.assertEqual(self.engine.quickSlot.state, "stopped")
        self.engine.silenceAlarm.assert_called_once()


class TestPackageMetadataAndAssets(unittest.TestCase):
    """Verifies integrity of build configuration and embedded audio files."""

    def test_build_vars_contains_required_manifest_metadata(self):
        info = buildVars.addon_info
        self.assertEqual(info["addon_name"], "tymer")
        self.assertEqual(info["addon_version"], "2026.1")
        self.assertEqual(info["addon_minimumNVDAVersion"], "2024.1.0")
        self.assertEqual(info["addon_lastTestedNVDAVersion"], "2026.2.0")
        self.assertIn("Kamal Yaser", info["addon_author"])

    def test_embedded_wave_alert_files_exist_and_are_non_empty(self):
        self.assertTrue(os.path.isfile(paths.ALARM_SOUND_PATH))
        self.assertGreater(os.path.getsize(paths.ALARM_SOUND_PATH), 1000)

    def test_all_pot_strings_are_translated_in_arabic_po(self):
        def parse_po_entries(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            entries = {}
            current_id = None
            current_str = None
            in_id = False
            in_str = False
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("msgid "):
                    if current_id is not None:
                        entries[current_id] = current_str or ""
                    current_id = line[6:].strip().strip('"')
                    current_str = None
                    in_id = True
                    in_str = False
                elif line.startswith("msgstr "):
                    current_str = line[7:].strip().strip('"')
                    in_id = False
                    in_str = True
                elif line.startswith('"') and line.endswith('"'):
                    val = line[1:-1]
                    if in_id:
                        current_id += val
                    elif in_str:
                        current_str = (current_str or "") + val
            if current_id is not None:
                entries[current_id] = current_str or ""
            return entries

        base_dir = os.path.dirname(os.path.abspath(__file__))
        pot_path = os.path.join(base_dir, "tymer.pot")
        po_path = os.path.join(
            base_dir, "addon", "locale", "ar", "LC_MESSAGES", "nvda.po"
        )
        self.assertTrue(os.path.isfile(pot_path), "tymer.pot does not exist")
        self.assertTrue(os.path.isfile(po_path), "nvda.po does not exist")

        pot_entries = parse_po_entries(pot_path)
        po_entries = parse_po_entries(po_path)

        missing = [mid for mid in pot_entries if mid and mid not in po_entries]
        untranslated = [
            mid for mid in pot_entries if mid and not po_entries.get(mid, "").strip()
        ]

        self.assertEqual(missing, [], f"Missing translations in nvda.po: {missing}")
        self.assertEqual(
            untranslated, [], f"Untranslated strings in nvda.po: {untranslated}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
