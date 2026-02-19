from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "kaleidescape_strato"
DEFAULT_NAME = "Kaleidescape Strato"
DEFAULT_PORT = 10000
DEFAULT_TIMEOUT = 5.0
SENSOR_SCAN_INTERVAL = 5
CONF_DEBUG_COMMANDS = "debug_commands"
DEFAULT_DEBUG_COMMANDS = False
DATA_IS_MOVIE_PLAYER = "is_movie_player"
DATA_DEVICE_TYPE = "device_type"
PLATFORMS: list[Platform] = [Platform.REMOTE, Platform.SENSOR]

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
    "power_on": "LEAVE_STANDBY",
    "turn_on": "LEAVE_STANDBY",
    "on": "LEAVE_STANDBY",
    "power_off": "ENTER_STANDBY",
    "turn_off": "ENTER_STANDBY",
    "off": "ENTER_STANDBY",
}
