from site_scons.site_tools.NVDATool.typings import (
    AddonInfo,
    BrailleTables,
    SymbolDictionaries,
)
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
    addon_name="tymer",
    addon_summary=_("Tymer"),
    addon_description=_(
        """A modal command layer countdown timer add-on for NVDA providing 5 customizable timer slots with sound and speech alerts."""
    ),
    addon_version="2026.1",
    addon_changelog=_(
        """- Version 2026.1: Initial release with 5-slot countdown timers, one-shot modal command layer, quad actions, and NVDA settings panel."""
    ),
    addon_author="Kamal Yaser <kamalyaser31@gmail.com>",
    addon_url="https://github.com/kamalyaser31/tymer",
    addon_sourceURL="https://github.com/kamalyaser31/tymer",
    addon_docFileName="readme.html",
    addon_minimumNVDAVersion="2024.1.0",
    addon_lastTestedNVDAVersion="2026.2.0",
    addon_updateChannel=None,
    addon_license="GPL v2",
    addon_licenseURL="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
)

pythonSources = ["addon/**/*.py"]
i18nSources: list[str] = pythonSources + ["buildVars.py"]
excludedFiles: list[str] = []
baseLanguage: str = "en"
markdownExtensions: list[str] = []
brailleTables: BrailleTables = {}
symbolDictionaries: SymbolDictionaries = {}
speechDictionaries: dict = {}
