from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COMMAND_ALIASES, DEFAULT_NAME, DOMAIN


def _normalize_command(command: str) -> str:
    lowered = command.strip().lower()
    return COMMAND_ALIASES.get(lowered, command.strip())


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([KaleidescapeRemoteEntity(entry, client)])


class KaleidescapeRemoteEntity(RemoteEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_supported_features = RemoteEntityFeature.SEND_COMMAND

    def __init__(self, entry: ConfigEntry, client) -> None:
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_remote"
        self._attr_is_on = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "manufacturer": "Kaleidescape",
            "model": "Strato",
            "name": self._entry.data.get(CONF_NAME, DEFAULT_NAME),
        }

    async def async_send_command(self, command: Iterable[str] | str, **kwargs: Any) -> None:
        commands = [command] if isinstance(command, str) else list(command)

        num_repeats = int(kwargs.get("num_repeats", 1))
        delay_secs = float(kwargs.get("delay_secs", 0.4))

        for repeat_index in range(num_repeats):
            for command_index, raw_command in enumerate(commands):
                resolved = _normalize_command(raw_command)
                await self._client.async_send_command(resolved)

                last_command = command_index == len(commands) - 1
                last_repeat = repeat_index == num_repeats - 1
                if not (last_command and last_repeat):
                    await asyncio.sleep(delay_secs)
