from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from kaleidescape import Device as KaleidescapeDevice
from kaleidescape import KaleidescapeError
from kaleidescape import __version__ as _PYKALEIDESCAPE_VERSION
from kaleidescape import device as _kaleidescape_device

from .api import KaleidescapeRawClient
from .const import (
    CONF_ALLOW_RAW_COMMANDS,
    CONF_DEBUG_COMMANDS,
    DEFAULT_ALLOW_RAW_COMMANDS,
    DEFAULT_DEBUG_COMMANDS,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    PLATFORMS,
)


def _patched_pkg_version(*_args: object, **_kwargs: object) -> str:
    """Return the pinned pykaleidescape version without touching the filesystem."""
    return _PYKALEIDESCAPE_VERSION


# pykaleidescape 1.1.6 calls importlib.metadata.version() during device.connect(),
# a blocking disk read in the event loop. Fixed upstream but unreleased.
_kaleidescape_device.pkg_version = _patched_pkg_version


@dataclass
class KaleidescapeRuntimeData:
    """Runtime data for a Kaleidescape config entry."""

    device: KaleidescapeDevice
    raw_client: KaleidescapeRawClient
    allow_raw_commands: bool


type KaleidescapeConfigEntry = ConfigEntry[KaleidescapeRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> bool:
    """Set up Kaleidescape from a config entry."""
    host = entry.data[CONF_HOST]
    device = KaleidescapeDevice(
        host, timeout=DEFAULT_TIMEOUT, reconnect=True, reconnect_delay=DEFAULT_TIMEOUT
    )

    try:
        await device.connect()
    except (KaleidescapeError, ConnectionError) as err:
        await device.disconnect()
        raise ConfigEntryNotReady(f"Unable to connect to {host}: {err}") from err

    debug_commands = entry.options.get(CONF_DEBUG_COMMANDS, DEFAULT_DEBUG_COMMANDS)
    raw_client = KaleidescapeRawClient(
        host=host,
        port=DEFAULT_PORT,
        timeout=DEFAULT_TIMEOUT,
        debug_commands=debug_commands,
    )

    entry.runtime_data = KaleidescapeRuntimeData(
        device=device,
        raw_client=raw_client,
        allow_raw_commands=entry.options.get(
            CONF_ALLOW_RAW_COMMANDS, DEFAULT_ALLOW_RAW_COMMANDS
        ),
    )

    async def disconnect(event: Event) -> None:
        await device.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, disconnect)
    )
    entry.async_on_unload(device.disconnect)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: KaleidescapeConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: KaleidescapeConfigEntry
) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


@dataclass
class KaleidescapeDeviceInfo:
    """Metadata for a Kaleidescape device."""

    host: str
    serial: str
    name: str
    model: str
    server_only: bool


class UnsupportedError(HomeAssistantError):
    """Error for unsupported device types."""


async def validate_host(host: str) -> KaleidescapeDeviceInfo:
    """Validate device host."""
    device = KaleidescapeDevice(host)

    try:
        await device.connect()
    except (KaleidescapeError, ConnectionError):
        await device.disconnect()
        raise

    info = KaleidescapeDeviceInfo(
        host=device.host,
        serial=device.system.serial_number,
        name=device.system.friendly_name,
        model=device.system.type,
        server_only=device.is_server_only,
    )

    await device.disconnect()

    return info
