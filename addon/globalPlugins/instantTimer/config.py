# -*- coding: utf-8 -*-
# Instant Timer Add-on for NVDA
# Author: Kamal Yaser <kamalyaser31@gmail.com>

import copy
import json
import os
from typing import Any, Dict, Optional

try:
    from logHandler import log
except ImportError:
    import logging

    log = logging.getLogger("instantTimer")
    if not hasattr(log, "debugWarning"):
        log.debugWarning = log.warning

CONFIG_FILENAME = "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "notificationStyle": 0,
    "verbosity": 0,
    "entryBeep": True,
    "preExpiryCue": False,
    "preExpirySeconds": 10,
    "restartPolicy": "resume",
    "defaultDurations": [300, 600, 900, 1500, 3600],
    "slotLabels": ["", "", "", "", ""],
    "activeTimersData": ["", "", "", "", ""],
}


def getConfigPath() -> str:
    """Return the absolute path to config.json in user's active NVDA config directory."""
    try:
        import globalVars

        base = globalVars.appArgs.configPath
    except (ImportError, AttributeError):
        base = None
    if not base:
        base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda")
    return os.path.join(base, "instantTimer", CONFIG_FILENAME)


def _sanitizeConfig(conf: Dict[str, Any]) -> Dict[str, Any]:
    """Validate external deserialized config at boundary and clamp to safe bounds."""
    if conf.get("notificationStyle") not in (0, 1, 2):
        conf["notificationStyle"] = DEFAULT_CONFIG["notificationStyle"]

    if conf.get("verbosity") not in (0, 1):
        conf["verbosity"] = DEFAULT_CONFIG["verbosity"]

    conf["entryBeep"] = bool(conf.get("entryBeep", True))
    conf["preExpiryCue"] = bool(conf.get("preExpiryCue", False))

    try:
        lead = int(conf.get("preExpirySeconds", 10))
        conf["preExpirySeconds"] = max(1, min(300, lead))
    except (ValueError, TypeError):
        conf["preExpirySeconds"] = 10

    if conf.get("restartPolicy") not in ("resume", "reset", "pause"):
        conf["restartPolicy"] = "resume"

    durs = conf.get("defaultDurations")
    if not isinstance(durs, list) or len(durs) != 5:
        conf["defaultDurations"] = list(DEFAULT_CONFIG["defaultDurations"])
    else:
        cleaned_durs = []
        for i, d in enumerate(durs):
            try:
                cleaned_durs.append(max(1, int(d)))
            except (ValueError, TypeError):
                cleaned_durs.append(DEFAULT_CONFIG["defaultDurations"][i])
        conf["defaultDurations"] = cleaned_durs

    labels = conf.get("slotLabels")
    if not isinstance(labels, list) or len(labels) != 5:
        conf["slotLabels"] = list(DEFAULT_CONFIG["slotLabels"])
    else:
        conf["slotLabels"] = [
            str(lbl).strip() if lbl is not None else "" for lbl in labels
        ]

    sessions = conf.get("activeTimersData")
    if not isinstance(sessions, list) or len(sessions) != 5:
        conf["activeTimersData"] = list(DEFAULT_CONFIG["activeTimersData"])
    else:
        conf["activeTimersData"] = [str(s) if s is not None else "" for s in sessions]

    return conf


def loadConfig(path: Optional[str] = None) -> Dict[str, Any]:
    """Safely load configuration from JSON file, merging with default values."""
    target_path = path or getConfigPath()
    conf = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.isfile(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k, v in data.items():
                    if k in conf:
                        conf[k] = v
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
            pass
    return _sanitizeConfig(conf)


def saveConfig(conf: Dict[str, Any], path: Optional[str] = None) -> None:
    """Safely write configuration dictionary to JSON file."""
    target_path = path or getConfigPath()
    config_dir = os.path.dirname(target_path)
    if config_dir:
        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError:
            pass
    sanitized = _sanitizeConfig(conf)
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, ensure_ascii=False, indent="\t")
    except OSError:
        log.debugWarning("Instant Timer: Failed to write configuration", exc_info=True)
