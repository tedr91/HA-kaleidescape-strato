from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_DEVICE_TYPE, DATA_IS_MOVIE_PLAYER, DEFAULT_NAME, DOMAIN
from .coordinator import KaleidescapeSensorCoordinator


@dataclass(frozen=True, kw_only=True)
class KaleidescapeSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, str | int | float | None]], StateType]


SHARED_SENSOR_TYPES: tuple[KaleidescapeSensorDescription, ...] = (
    KaleidescapeSensorDescription(
        key="system_readiness_state",
        name="System readiness state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("system_readiness_state"),
    ),
    KaleidescapeSensorDescription(
        key="power_state",
        name="Power state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("power_state"),
    ),
)


PLAYER_SENSOR_TYPES: tuple[KaleidescapeSensorDescription, ...] = (
    KaleidescapeSensorDescription(
        key="media_location",
        name="Media location",
        value_fn=lambda state: state.get("media_location"),
    ),
    KaleidescapeSensorDescription(
        key="play_status",
        name="Play status",
        value_fn=lambda state: state.get("play_status"),
    ),
    KaleidescapeSensorDescription(
        key="play_speed",
        name="Play speed",
        value_fn=lambda state: state.get("play_speed"),
    ),
    KaleidescapeSensorDescription(
        key="video_mode",
        name="Video mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("video_mode"),
    ),
    KaleidescapeSensorDescription(
        key="video_color_eotf",
        name="Video color eotf",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("video_color_eotf"),
    ),
    KaleidescapeSensorDescription(
        key="video_color_space",
        name="Video color space",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("video_color_space"),
    ),
    KaleidescapeSensorDescription(
        key="video_color_depth",
        name="Video color depth",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("video_color_depth"),
    ),
    KaleidescapeSensorDescription(
        key="video_color_sampling",
        name="Video color sampling",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("video_color_sampling"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_ratio",
        name="Screen mask ratio",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("screen_mask_ratio"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_top_trim_rel",
        name="Screen mask top trim rel",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.get("screen_mask_top_trim_rel"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_bottom_trim_rel",
        name="Screen mask bottom trim rel",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.get("screen_mask_bottom_trim_rel"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_conservative_ratio",
        name="Screen mask conservative ratio",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("screen_mask_conservative_ratio"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_top_mask_abs",
        name="Screen mask top mask abs",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.get("screen_mask_top_mask_abs"),
    ),
    KaleidescapeSensorDescription(
        key="screen_mask_bottom_mask_abs",
        name="Screen mask bottom mask abs",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.get("screen_mask_bottom_mask_abs"),
    ),
    KaleidescapeSensorDescription(
        key="cinemascape_mode",
        name="Cinemascape mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("cinemascape_mode"),
    ),
    KaleidescapeSensorDescription(
        key="cinemascape_mask",
        name="Cinemascape mask",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("cinemascape_mask"),
    ),
    KaleidescapeSensorDescription(
        key="ui_screen",
        name="Ui screen",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("ui_screen"),
    ),
    KaleidescapeSensorDescription(
        key="ui_popup",
        name="Ui popup",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("ui_popup"),
    ),
    KaleidescapeSensorDescription(
        key="ui_dialog",
        name="Ui dialog",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("ui_dialog"),
    ),
    KaleidescapeSensorDescription(
        key="title_location",
        name="Title location",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("title_location"),
    ),
    KaleidescapeSensorDescription(
        key="title_length",
        name="Title length",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("title_length"),
    ),
    KaleidescapeSensorDescription(
        key="chapter_location",
        name="Chapter location",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("chapter_location"),
    ),
    KaleidescapeSensorDescription(
        key="chapter_length",
        name="Chapter length",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.get("chapter_length"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: KaleidescapeSensorCoordinator = hass.data[DOMAIN][entry.entry_id][
        "sensor_coordinator"
    ]
    is_movie_player: bool = hass.data[DOMAIN][entry.entry_id][DATA_IS_MOVIE_PLAYER]

    sensor_types = SHARED_SENSOR_TYPES
    if is_movie_player:
        sensor_types += PLAYER_SENSOR_TYPES

    async_add_entities(
        KaleidescapeSensorEntity(entry, coordinator, description) for description in sensor_types
    )


class KaleidescapeSensorEntity(CoordinatorEntity[KaleidescapeSensorCoordinator], SensorEntity):
    _attr_has_entity_name = True

    entity_description: KaleidescapeSensorDescription

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: KaleidescapeSensorCoordinator,
        description: KaleidescapeSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

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
    def native_value(self) -> StateType:
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
