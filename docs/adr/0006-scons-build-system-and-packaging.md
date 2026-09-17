# SCons Build System, Addon Layout, and Localization Architecture

## Context
Standard NVDA add-ons require reliable packaging into `.nvda-addon` bundles, automated gettext extraction (`.pot`), documentation compilation (Markdown to HTML), and standardized metadata management across locales.

## Decision
1. **SCons Template Standard**: We adopt the official NVDA add-on SCons build template (`sconstruct`, `site_scons`, `buildVars.py`, `manifest.ini.tpl`, `manifest-translated.ini.tpl`).
2. **Directory Restructuring**: All runtime plugin code resides under `addon/` at the root:
   - `addon/globalPlugins/tymer/`: Core plugin code and assets.
   - `addon/doc/ar/` and `addon/doc/en/`: Localized documentation in Markdown.
   - `addon/locale/ar/LC_MESSAGES/`: Gettext `.po` catalogs.
3. **Build Lifecycle**:
   - `scons pot`: Extracts all localized strings.
   - `scons`: Compiles `.po` to `.mo`, converts `readme.md` to `readme.html`, generates `manifest.ini`, and outputs `tymer-<version>.nvda-addon`.
4. **Publishing**: GitHub release automation via `gh repo create` and `gh release create`.

## Status
Accepted
