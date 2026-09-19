# Changelog

All notable changes to the Instant Timer add-on will be documented in this file.

## [2026.1-dev] - 2026-09-19
- fix(core): remediate clean-code-guard and test-guard audit findings: fix entryBeep config lookup in __init__.py, guard secure desktop mode, support debugWarning in fallback logger, qualify plugin module matching, purge mock illusions from run_tests.py, and expand behavioral tests to 48 passing tests (100% green).
- feat(config): migrate settings, durations, and session persistence to standalone local JSON config (`config.json`) following instantAccess pattern, verified with 44 passing unit tests under clean-code-guard.
- refactor(project): rename add-on to Instant Timer (`instantTimer`, `المؤقت الفوري`), change layer shortcut to `NVDA+E`, update configuration namespace to `instantTimer`, and package `instantTimer-2026.1.nvda-addon`.
- feat(settings): configure warning cue lead time in seconds (1-300s, default 10) from NVDA settings panel with dynamic toggle, and apply humanizer purification to all project prose and Arabic translations.
- feat(keys): swap Shift and Alt key actions across all command layers (presets 1-5, quick timer Q, stopwatch S): Shift now resets to stopped/zero, and Alt now pauses or resumes countdown/stopwatch.
- docs(guard): resolved docs-guard finding by replacing missing `COPYING.txt` reference with official GNU GPL v2 URL across all documentation files and setting `addon_licenseURL` in `buildVars.py`.
- release(addon): audited all translations, verified documentation parity across Arabic and English, added automated PO coverage test to run_tests.py (39 tests passing), and compiled final package `tymer-2026.1.nvda-addon` via SCons.
- refactor(clean-code): comprehensive DRY purification across dialogs, gesture handlers, configuration readers, stopwatch re-execution, and SRP onOk extraction under clean-code-guard.
- refactor(timer): purge obsolete 'expired' slot state, dead report branches, and redundant translation entries.
- feat(timer): auto-reset countdown timer slot to stopped initial state immediately upon expiration.
- fix(i18n): merge duplicate "Tymer" msgid definitions in `addon/locale/ar/LC_MESSAGES/nvda.po` to resolve `msgfmt` fatal compilation error.
- build(addon): successfully compiled translations and built release package `tymer-2026.1.nvda-addon` via SCons.
- fix(core): resolve configuration validation fallback, inverted save logic, mnemonic collision, and implement demand-driven ticker with engine synchronization.
- Conducted dual-axis code review (/code-review and /code-review-skill) covering Standards and Spec compliance.
- Fixed critical name-mangling bug in `GlobalPlugin.finish()` by replacing `self.__gestures` with explicit `self.bindGesture("kb:NVDA+y", "tymerLayerCommands")`.
- Refined `formatTime` to properly differentiate singular and plural time components.
- Removed redundant `initTranslation()` call from `paths.py`.
- Expanded test suite to 28 passing tests in `run_tests.py` verifying layer finish rebinding.
- Refactored `run_tests.py` under `/test-guard` guidelines: eliminated duplicate normalization logic, bound tests to real `GlobalPlugin._getGestureKey`, and consolidated parameterized cases with `subTest`.
- Replaced 5-second alarm audio with a clean 0.8s (1-second) CC0 public domain chime, adjusted auto-stop timer to 1000ms, and resolved clean-code-guard findings across all modules.
- Removed long/unwanted `cue.wav` asset and `CUE_SOUND_PATH` constant to maintain a lean distribution package.
- Added lightweight in-memory digital Stopwatch (`Stopwatch`) mapped to `S`, `Shift+S`, `Control+S`, and `Alt+S` in the command layer with distinct audio tone cues and adaptive digital time reporting.

## [1.0.0-planning] - 2026-09-17
- Established comprehensive architectural design, 6 ADRs, CONTEXT.md domain glossary, 12 reference patterns from clock add-on, implementation blueprint, 7-ticket Wayfinder dependency map, and full SCons build template integration (`sconstruct`, `buildVars.py`, `site_scons`, manifest templates, `.gitignore`).
