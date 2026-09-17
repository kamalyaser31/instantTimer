# -*- coding: utf-8 -*-
# Tymer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

import os
from typing import Final
import addonHandler

PLUGIN_DIR: Final = os.path.join(
    addonHandler.getCodeAddon().path, "globalPlugins", "tymer"
)
SOUNDS_DIR: Final = os.path.join(PLUGIN_DIR, "waves")
ALARM_SOUND_PATH: Final = os.path.join(SOUNDS_DIR, "alarm.wav")
