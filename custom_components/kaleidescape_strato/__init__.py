from __future__ import annotations

import logging
from typing import Any

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

KaleidescapeConfigEntry = ConfigEntry

_LOGGER = logging.getLogger(__name__)
DATA_LOADED_PLATFORMS = "loaded_platforms"


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

    loaded_platforms: list[Any] = []
    for platform in PLATFORMS:
        try:
            await hass.config_entries.async_forward_entry_setups(entry, [platform])
            loaded_platforms.append(platform)
        except Exception:
            _LOGGER.exception(
                "Failed to set up Kaleidescape platform '%s' for entry %s",
                platform,
                entry.entry_id,
            )

    if not loaded_platforms:
        _LOGGER.error("No Kaleidescape platforms could be set up for entry %s", entry.entry_id)
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return False

    hass.data[DOMAIN][entry.entry_id][DATA_LOADED_PLATFORMS] = loaded_platforms
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> bool:
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    loaded_platforms = entry_data.get(DATA_LOADED_PLATFORMS, PLATFORMS)
    unloaded = await hass.config_entries.async_unload_platforms(entry, loaded_platforms)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
