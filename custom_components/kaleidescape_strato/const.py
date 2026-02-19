from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "kaleidescape_strato"
DEFAULT_NAME = "Kaleidescape"
DEFAULT_PORT = 10000
DEFAULT_TIMEOUT = 5.0
SENSOR_SCAN_INTERVAL = 5
CONF_DEBUG_COMMANDS = "debug_commands"
DEFAULT_DEBUG_COMMANDS = False
CONF_ALLOW_RAW_COMMANDS = "allow_raw_commands"
DEFAULT_ALLOW_RAW_COMMANDS = False
DATA_IS_MOVIE_PLAYER = "is_movie_player"
DATA_DEVICE_TYPE = "device_type"
PLATFORMS: list[Platform] = [Platform.REMOTE, Platform.SENSOR, Platform.MEDIA_PLAYER]

COMMAND_ALIASES: dict[str, str] = {
    "up": "UP",
    "down": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "select": "SELECT",
    "ok": "SELECT",
    "enter": "SELECT",
    "back": "BACK",
    "cancel": "CANCEL",
    "exit": "BACK",
    "home": "HOME",
    "menu": "MENU",
    "play": "PLAY",
    "pause": "PAUSE",
    "stop": "STOP_OR_CANCEL",
    "next": "NEXT",
    "previous": "PREVIOUS",
    "rewind": "SCAN_REVERSE",
    "replay": "REPLAY",
    "fast_forward": "SCAN_FORWARD",
    "info": "INFO",
    "power_on": "LEAVE_STANDBY",
    "turn_on": "LEAVE_STANDBY",
    "on": "LEAVE_STANDBY",
    "power_off": "ENTER_STANDBY",
    "turn_off": "ENTER_STANDBY",
    "off": "ENTER_STANDBY",
    "intermission_on": "INTERMISSION_ON",
    "intermission_off": "INTERMISSION_OFF",
    "intermission_toggle": "INTERMISSION_TOGGLE",
    "intermission": "INTERMISSION_TOGGLE",
    "movie_list": "GO_MOVIE_LIST",
    "movie_collections": "GO_MOVIE_COLLECTIONS",
    "movie_covers": "GO_MOVIE_COVERS",
    "movies": "GO_MOVIE_COLLECTIONS",
    "system_status": "GO_SYSTEM_STATUS",
    "settings": "GO_SYSTEM_STATUS",
    "details": "DETAILS",
    "kaleidescape_menu_toggle": "KALEIDESCAPE_MENU_TOGGLE",
    "kaleidescape_menu_on": "KALEIDESCAPE_MENU_ON",
    "kaleidescape_menu_off": "KALEIDESCAPE_MENU_OFF",
    "navigation": "SHOW_NAVIGATION_OVERLAY",
    "navigation_overlay": "SHOW_NAVIGATION_OVERLAY",
    "shuffle_covers": "SHUFFLE_COVER_ART",
}
