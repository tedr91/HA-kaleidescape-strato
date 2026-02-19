from __future__ import annotations

from datetime import datetime

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import utcnow

from .const import DATA_DEVICE_TYPE, DATA_IS_MOVIE_PLAYER, DEFAULT_NAME, DOMAIN
from .coordinator import KaleidescapeSensorCoordinator

POWER_ON_COMMAND = "LEAVE_STANDBY"
POWER_OFF_COMMAND = "ENTER_STANDBY"

PLAYING_STATES = {"playing", "forward", "reverse"}


def _supported_features() -> int:
    features = 0
    for feature_name in (
        "TURN_ON",
        "TURN_OFF",
        "PLAY",
        "PAUSE",
        "STOP",
        "NEXT_TRACK",
        "PREVIOUS_TRACK",
    ):
        feature_value = getattr(MediaPlayerEntityFeature, feature_name, 0)
        features |= int(feature_value) if feature_value else 0
    return features


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    if not hass.data[DOMAIN][entry.entry_id][DATA_IS_MOVIE_PLAYER]:
        return

    client = hass.data[DOMAIN][entry.entry_id]["client"]
    coordinator: KaleidescapeSensorCoordinator = hass.data[DOMAIN][entry.entry_id][
        "sensor_coordinator"
    ]
    async_add_entities([KaleidescapeMediaPlayerEntity(entry, client, coordinator)])


class KaleidescapeMediaPlayerEntity(
    CoordinatorEntity[KaleidescapeSensorCoordinator], MediaPlayerEntity
):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = _supported_features()

    def __init__(
        self,
        entry: ConfigEntry,
        client,
        coordinator: KaleidescapeSensorCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_media_player"

    @property
    def device_info(self):
        device_type = self.hass.data[DOMAIN][self._entry.entry_id].get(
            DATA_DEVICE_TYPE, "Kaleidescape"
        )
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "manufacturer": "Kaleidescape",
            "model": str(device_type),
            "name": self._entry.data.get(CONF_NAME, DEFAULT_NAME),
        }

    @property
    def state(self) -> MediaPlayerState:
        if not self.coordinator.data:
            return MediaPlayerState.OFF

        power_state = str(self.coordinator.data.get("power_state") or "standby")
        if power_state == "standby":
            return MediaPlayerState.OFF

        play_status = str(self.coordinator.data.get("play_status") or "none")
        if play_status in PLAYING_STATES:
            return MediaPlayerState.PLAYING
        if play_status == "paused":
            return MediaPlayerState.PAUSED
        return MediaPlayerState.IDLE

    @property
    def media_position(self) -> int | None:
        if not self.coordinator.data:
            return None
        location = self.coordinator.data.get("title_location")
        if isinstance(location, (int, float)):
            return int(location)
        return None

    @property
    def media_duration(self) -> int | None:
        if not self.coordinator.data:
            return None
        duration = self.coordinator.data.get("title_length")
        if isinstance(duration, (int, float)):
            return int(duration)
        return None

    @property
    def media_position_updated_at(self) -> datetime | None:
        if self.state == MediaPlayerState.PLAYING:
            return utcnow()
        return None

    async def async_turn_on(self) -> None:
        await self._client.async_send_command(POWER_ON_COMMAND)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self._client.async_send_command(POWER_OFF_COMMAND)
        await self.coordinator.async_request_refresh()

    async def async_media_play(self) -> None:
        await self._client.async_send_command("PLAY")
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        await self._client.async_send_command("PAUSE")
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        await self._client.async_send_command("STOP_OR_CANCEL")
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        await self._client.async_send_command("NEXT")
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        await self._client.async_send_command("PREVIOUS")
        await self.coordinator.async_request_refresh()

    async def async_toggle(self) -> None:
        if self.state == MediaPlayerState.PLAYING:
            await self.async_media_pause()
            return
        await self.async_media_play()

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()
