from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from kaleidescape import const as kaleidescape_const

from . import KaleidescapeConfigEntry
from .api import KaleidescapeRawClient
from .const import ALIAS_TO_METHOD, COMMAND_ALIASES
from .entity import KaleidescapeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KaleidescapeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform from a config entry."""
    data = entry.runtime_data
    async_add_entities(
        [KaleidescapeRemote(data.device, data.raw_client, data.allow_raw_commands)]
    )


class KaleidescapeRemote(KaleidescapeEntity, RemoteEntity):
    """Representation of a Kaleidescape device."""

    _attr_name = None

    def __init__(
        self,
        device,
        raw_client: KaleidescapeRawClient,
        allow_raw_commands: bool,
    ) -> None:
        super().__init__(device)
        self._raw_client = raw_client
        self._allow_raw_commands = allow_raw_commands

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._device.power.state == kaleidescape_const.DEVICE_POWER_STATE_ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self._device.leave_standby()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self._device.enter_standby()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the device."""
        commands = list(command)
        num_repeats = int(kwargs.get("num_repeats", 1))
        delay_secs = float(kwargs.get("delay_secs", 0.4))

        for repeat_index in range(num_repeats):
            for command_index, cmd in enumerate(commands):
                await self._async_send_single(cmd)

                last_command = command_index == len(commands) - 1
                last_repeat = repeat_index == num_repeats - 1
                if not (last_command and last_repeat):
                    await asyncio.sleep(delay_secs)

    async def _async_send_single(self, cmd: str) -> None:
        """Resolve and send a single command."""
        key = cmd.strip().lower()

        method_name = ALIAS_TO_METHOD.get(key)
        if method_name is not None:
            await getattr(self._device, method_name)()
            return

        wire_command = COMMAND_ALIASES.get(key)
        if wire_command is not None:
            await self._raw_client.async_send_command(wire_command)
            return

        if self._allow_raw_commands:
            await self._raw_client.async_send_command(cmd.strip())
            return

        raise HomeAssistantError(
            f"{cmd} is not a known command. Enable 'Allow sending raw commands to "
            "device' in options to send passthrough commands."
        )
