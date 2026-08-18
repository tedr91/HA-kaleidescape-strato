from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
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
    DOMAIN,
    PLATFORMS,
)
from .migration import _migrated_unique_id, is_legacy_unique_id

_LOGGER = logging.getLogger(__name__)


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


async def async_migrate_entry(
    hass: HomeAssistant, entry: KaleidescapeConfigEntry
) -> bool:
    """Migrate legacy config entry, entity, and device registry identities."""
    if entry.version >= 2:
        return True

    device_registry = dr.async_get(hass)
    serial = next(
        (
            identifier
            for device in dr.async_entries_for_config_entry(
                device_registry, entry.entry_id
            )
            for domain, identifier in device.identifiers
            if domain == DOMAIN and identifier != entry.entry_id
        ),
        None,
    )

    if serial is None and entry.unique_id and not is_legacy_unique_id(entry.unique_id):
        serial = entry.unique_id

    if serial is None and (host := entry.data.get(CONF_HOST)):
        try:
            info = await validate_host(host)
        except Exception:  # noqa: BLE001
            pass
        else:
            serial = info.serial

    if not serial:
        _LOGGER.warning(
            "Unable to resolve the serial number while migrating config entry %s",
            entry.entry_id,
        )
        return False

    entity_registry = er.async_get(hass)
    existing_keys = {
        (entity.domain, entity.platform, entity.unique_id)
        for entity in er.async_entries_for_config_entry(
            entity_registry, entry.entry_id
        )
    }
    collisions: set[str] = set()

    def migrate_entity(entity: er.RegistryEntry) -> dict[str, str] | None:
        new_unique_id = _migrated_unique_id(
            entity.domain, entity.unique_id, entry.entry_id, serial
        )
        if new_unique_id is None:
            return None
        if (entity.domain, entity.platform, new_unique_id) in existing_keys:
            collisions.add(entity.entity_id)
            return None
        return {"new_unique_id": new_unique_id}

    await er.async_migrate_entries(hass, entry.entry_id, migrate_entity)
    for entity_id in collisions:
        entity_registry.async_remove(entity_id)

    legacy_device = device_registry.async_get_device(
        identifiers={(DOMAIN, entry.entry_id)}
    )
    current_device = device_registry.async_get_device(
        identifiers={(DOMAIN, serial)}
    )
    if legacy_device is not None and current_device is None:
        device_registry.async_update_device(
            legacy_device.id, new_identifiers={(DOMAIN, serial)}
        )
    elif (
        legacy_device is not None
        and current_device is not None
        and legacy_device.id != current_device.id
    ):
        for entity in er.async_entries_for_device(
            entity_registry, legacy_device.id, include_disabled_entities=True
        ):
            entity_registry.async_update_entity(
                entity.entity_id, device_id=current_device.id
            )
        device_registry.async_remove_device(legacy_device.id)

    hass.config_entries.async_update_entry(
        entry, unique_id=serial, version=2
    )
    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: KaleidescapeConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow stale devices to be removed while protecting a verified live device."""
    live: set[tuple[str, str]] = set()
    if config_entry.unique_id and not is_legacy_unique_id(config_entry.unique_id):
        live.add((DOMAIN, config_entry.unique_id))

    runtime = getattr(config_entry, "runtime_data", None)
    if runtime is not None and (serial := runtime.device.serial_number):
        live.add((DOMAIN, serial))

    return not (device_entry.identifiers & live)


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
