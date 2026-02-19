from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import KaleidescapeClient
from .const import (
    CONF_DEBUG_COMMANDS,
    DATA_DEVICE_TYPE,
    DATA_IS_MOVIE_PLAYER,
    DEFAULT_DEBUG_COMMANDS,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import KaleidescapeSensorCoordinator

type KaleidescapeConfigEntry = ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = KaleidescapeClient(
        host=entry.data["host"],
        port=entry.data.get("port", DEFAULT_PORT),
        timeout=entry.data.get("timeout", DEFAULT_TIMEOUT),
        debug_commands=entry.options.get(CONF_DEBUG_COMMANDS, DEFAULT_DEBUG_COMMANDS),
    )
    is_movie_player = True
    device_type = "Kaleidescape"
    try:
        is_movie_player, device_type = await client.async_get_device_profile()
    except Exception:
        _LOGGER.debug("Unable to detect Kaleidescape device profile at setup", exc_info=True)

    coordinator = KaleidescapeSensorCoordinator(
        hass,
        entry,
        client,
        include_player_metrics=is_movie_player,
    )
    try:
        await coordinator.async_refresh()
    except Exception:
        _LOGGER.debug("Initial Kaleidescape sensor refresh failed", exc_info=True)

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "sensor_coordinator": coordinator,
        DATA_IS_MOVIE_PLAYER: is_movie_player,
        DATA_DEVICE_TYPE: device_type,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
