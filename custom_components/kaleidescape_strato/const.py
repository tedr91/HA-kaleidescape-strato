from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "kaleidescape_strato"
DEFAULT_NAME = "Kaleidescape Strato"
DEFAULT_PORT = 10000
DEFAULT_TIMEOUT = 5.0
PLATFORMS: list[Platform] = [Platform.REMOTE]

COMMAND_ALIASES: dict[str, str] = {
    "up": "UP",
    "down": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "select": "SELECT",
    "ok": "SELECT",
    "enter": "SELECT",
    "back": "BACK",
    "exit": "BACK",
    "home": "HOME",
    "menu": "MENU",
    "play": "PLAY",
    "pause": "PAUSE",
    "stop": "STOP",
    "next": "NEXT",
    "previous": "PREVIOUS",
    "rewind": "SCAN_REVERSE",
    "fast_forward": "SCAN_FORWARD",
    "info": "INFO",
}
