# -*- coding: utf-8 -*-
# Instant Timer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

import os
from typing import Final
import addonHandler

PLUGIN_DIR: Final = os.path.join(
    addonHandler.getCodeAddon().path, "globalPlugins", "instantTimer"
)
SOUNDS_DIR: Final = os.path.join(PLUGIN_DIR, "waves")
ALARM_SOUND_PATH: Final = os.path.join(SOUNDS_DIR, "alarm.wav")
