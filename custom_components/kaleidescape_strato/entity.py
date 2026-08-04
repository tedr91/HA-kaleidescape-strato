from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, NAME

if TYPE_CHECKING:
    from kaleidescape import Device as KaleidescapeDevice

_LOGGER = logging.getLogger(__name__)


class KaleidescapeEntity(Entity):
    """Defines a base Kaleidescape entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, device: KaleidescapeDevice) -> None:
        self._device = device
        self._attr_unique_id = device.serial_number
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            name=f"{NAME} {device.system.friendly_name}",
            model=device.system.type,
            manufacturer=NAME,
            sw_version=f"{device.system.kos_version}",
            suggested_area="Theater",
            configuration_url=f"http://{device.host}",
        )

    async def async_added_to_hass(self) -> None:
        @callback
        def _update(event: str, *args: Any) -> None:
            self.async_write_ha_state()

        self.async_on_remove(self._device.dispatcher.connect(_update).disconnect)
