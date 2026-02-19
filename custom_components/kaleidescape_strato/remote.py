from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COMMAND_ALIASES,
    CONF_ALLOW_RAW_COMMANDS,
    DEFAULT_ALLOW_RAW_COMMANDS,
    DEFAULT_NAME,
    DOMAIN,
)

POWER_ON_COMMAND = "LEAVE_STANDBY"
POWER_OFF_COMMAND = "ENTER_STANDBY"


def _supported_features() -> int:
    features = 0
    for feature_name in ("SEND_COMMAND", "TURN_ON", "TURN_OFF", "TOGGLE"):
        feature_value = getattr(RemoteEntityFeature, feature_name, 0)
        features |= int(feature_value) if feature_value else 0
    return features


def _normalize_command(command: str, *, allow_raw_commands: bool) -> str:
    lowered = command.strip().lower()
    if lowered in COMMAND_ALIASES:
        return COMMAND_ALIASES[lowered]

    if allow_raw_commands:
        return command.strip()

    raise HomeAssistantError(
        "Raw commands are disabled. Enable 'Allow sending raw commands to device' "
        "in options to use passthrough commands."
    )


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
    _attr_supported_features = _supported_features()

    def __init__(self, entry: ConfigEntry, client) -> None:
        self._entry = entry
        self._client = client
        self._allow_raw_commands = entry.options.get(
            CONF_ALLOW_RAW_COMMANDS,
            DEFAULT_ALLOW_RAW_COMMANDS,
        )
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
                resolved = _normalize_command(
                    raw_command,
                    allow_raw_commands=self._allow_raw_commands,
                )
                await self._client.async_send_command(resolved)

                last_command = command_index == len(commands) - 1
                last_repeat = repeat_index == num_repeats - 1
                if not (last_command and last_repeat):
                    await asyncio.sleep(delay_secs)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.async_send_command(POWER_ON_COMMAND)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.async_send_command(POWER_OFF_COMMAND)
        self._attr_is_on = False

    async def async_toggle(self, **kwargs: Any) -> None:
        if self._attr_is_on:
            await self.async_turn_off(**kwargs)
            return
        await self.async_turn_on(**kwargs)
