from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import KaleidescapeClient
from .const import DOMAIN, SENSOR_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

DEFAULT_PLAYBACK_STATE: dict[str, str | int | float] = {
    "serial": "",
    "cpdid": "",
    "device_ip": "",
    "media_location": "none",
    "play_status": "none",
    "play_speed": 0,
    "title_length": 0,
    "title_location": 0,
    "chapter_length": 0,
    "chapter_location": 0,
    "media_title": "",
    "media_content_id": "",
    "media_content_type": "none",
    "media_image_url": "",
    "video_mode": "none",
    "video_color_eotf": "unknown",
    "video_color_space": "default",
    "video_color_depth": "unknown",
    "video_color_sampling": "none",
    "screen_mask_ratio": "none",
    "screen_mask_top_trim_rel": 0.0,
    "screen_mask_bottom_trim_rel": 0.0,
    "screen_mask_conservative_ratio": "none",
    "screen_mask_top_mask_abs": 0.0,
    "screen_mask_bottom_mask_abs": 0.0,
    "cinemascape_mode": "none",
    "cinemascape_mask": 0,
    "system_readiness_state": "idle",
    "power_state": "standby",
    "ui_screen": "unknown",
    "ui_popup": "none",
    "ui_dialog": "none",
}


class KaleidescapeSensorCoordinator(DataUpdateCoordinator[dict[str, str | int | float | None]]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: KaleidescapeClient,
        *,
        include_player_metrics: bool,
    ) -> None:
        self._client = client
        self._include_player_metrics = include_player_metrics
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.entry_id}_sensors",
            update_interval=timedelta(seconds=SENSOR_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, str | int | float | None]:
        response = await self._client.async_query_playback_state(
            include_player_metrics=self._include_player_metrics
        )
        return {
            key: response.get(key)
            if response.get(key) is not None
            else DEFAULT_PLAYBACK_STATE[key]
            for key in DEFAULT_PLAYBACK_STATE
        }
