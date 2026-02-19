from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

PLAY_STATUS_INDEX = {
    0: "none",
    1: "paused",
    2: "playing",
    4: "forward",
    6: "reverse",
}

SYSTEM_READINESS_INDEX = {
    0: "ready",
    1: "becoming_ready",
    2: "idle",
}

POWER_STATE_INDEX = {
    0: "standby",
    1: "on",
}

UI_SCREEN_INDEX = {
    0: "unknown",
    1: "movie_list",
    2: "movie_collections",
    3: "movie_covers",
    4: "parental_control",
    7: "playing_movie",
    8: "system_status",
    9: "music_list",
    10: "music_covers",
    11: "music_collections",
    12: "music_now_playing",
    14: "vault_summary",
    15: "system_settings",
    16: "movie_store",
    17: "paired_unit_lobby",
}

UI_POPUP_INDEX = {
    0: "none",
    1: "details",
    2: "movie_status",
    3: "movie_not_status",
}

UI_DIALOG_INDEX = {
    0: "none",
    1: "menu",
    2: "passcode",
    3: "question",
    4: "information",
    5: "warning",
    6: "error",
    7: "preplay",
    8: "warranty",
    9: "keyboard",
    10: "ip_config",
}

VIDEO_MODE_INDEX = {
    0: "none",
    1: "480i60_4:3",
    2: "480i60_16:9",
    3: "480p60_4:3",
    4: "480p60_16:9",
    5: "576i50_4:3",
    6: "576i50_16:9",
    7: "576p50_4:3",
    8: "576p50_16:9",
    9: "720p60_ntsc_hd",
    10: "720p50_pal_hd",
    11: "1080i60_16:9",
    12: "1080i50_16:9",
    13: "1080p60_16:9",
    14: "1080p50_16:9",
    17: "1080p24_16:9",
    19: "480i60_64:27",
    20: "576i50_64:27",
    21: "1080i60_64:27",
    22: "1080i50_64:27",
    23: "1080p60_64:27",
    24: "1080p50_64:27",
    25: "1080p23976_64:27",
    26: "1080p24_64:27",
    27: "3840x2160p23976_16:9",
    28: "3840x2160p23976_64:27",
    29: "3840x2160p30_16:9",
    30: "3840x2160p30_64:27",
    31: "3840x2160p60_16:9",
    32: "3840x2160p60_64:27",
    33: "3840x2160p25_16:9",
    34: "3840x2160p25_64:27",
    35: "3840x2160p50_16:9",
    36: "3840x2160p50_64:27",
    37: "3840x2160p24_16:9",
    38: "3840x2160p24_64:27",
}

VIDEO_COLOR_EOTF_INDEX = {
    0: "unknown",
    1: "sdr",
    2: "hdr",
    3: "smtpest2084",
}

VIDEO_COLOR_SPACE_INDEX = {
    0: "default",
    1: "rgb",
    2: "bt601",
    3: "bt709",
    4: "bt2020",
}

VIDEO_COLOR_DEPTH_INDEX = {
    0: "unknown",
    24: "24bit",
    30: "30bit",
    36: "36bit",
}

VIDEO_COLOR_SAMPLING_INDEX = {
    0: "none",
    1: "rgb",
    2: "ycbcr422",
    3: "ycbcr444",
    4: "ycbcr420",
}

SCREEN_MASK_RATIO_INDEX = {
    0: "none",
    1: "1.33",
    2: "1.66",
    3: "1.78",
    4: "1.85",
    5: "2.35",
}

CINEMASCAPE_MODE_INDEX = {
    0: "none",
    1: "anamorphic",
    2: "letterbox",
    3: "native",
}

MOVIE_LOCATION_INDEX = {
    0: "none",
    3: "content",
    4: "intermission",
    5: "credits",
    6: "disc_menu",
}

_LOGGER = logging.getLogger(__name__)

LOCAL_CPDID = "01"


def _build_payload(command: str) -> bytes:
    normalized = command.strip()
    if "/" in normalized:
        wire_command = normalized
    else:
        wire_command = f"{LOCAL_CPDID}/0/{normalized.upper()}:"
    return f"{wire_command}\n".encode("latin-1")


@dataclass(frozen=True)
class KaleidescapeResponse:
    status: int
    name: str
    fields: list[str]


def _parse_response_message(message: str) -> KaleidescapeResponse | None:
    normalized = message.strip()
    if "/" not in normalized:
        return None

    try:
        _, _, payload = normalized.split("/", 2)
    except ValueError:
        return None

    if ":" not in payload:
        return None

    status_text, body = payload.split(":", 1)
    try:
        status = int(status_text)
    except ValueError:
        return None

    if "/" in body:
        body = body.rsplit("/", 1)[0]

    parts = body.split(":")
    if not parts:
        return None

    fields = parts[1:]
    if fields and fields[-1] == "":
        fields = fields[:-1]

    return KaleidescapeResponse(status=status, name=parts[0], fields=fields)


def _decode_index(value: str, index: dict[int, str]) -> str:
    try:
        return index.get(int(value), value)
    except ValueError:
        return value


def _parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


class KaleidescapeClient:
    def __init__(
        self,
        host: str,
        port: int,
        timeout: float,
        debug_commands: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._debug_commands = debug_commands

    async def async_can_connect(self) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            _LOGGER.debug("Unable to connect to Kaleidescape host %s:%s", self._host, self._port)
            return False

    async def async_send_command(self, command: str) -> None:
        await self.async_send_request(command)

    async def async_send_request(self, command: str) -> KaleidescapeResponse | None:
        return (await self.async_send_requests([command])).get(command)

    async def async_send_requests(
        self, commands: list[str]
    ) -> dict[str, KaleidescapeResponse | None]:
        responses: dict[str, KaleidescapeResponse | None] = {command: None for command in commands}
        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            for command in commands:
                payload = _build_payload(command)
                if self._debug_commands:
                    _LOGGER.info("Kaleidescape command send: %s", payload.decode("latin-1").strip())
                writer.write(payload)
                await writer.drain()

                response = await asyncio.wait_for(reader.readline(), timeout=self._timeout)
                if not response:
                    continue

                decoded_response = response.decode(errors="ignore").strip()
                if self._debug_commands:
                    _LOGGER.info("Kaleidescape command response: %s", decoded_response)
                else:
                    _LOGGER.debug("Kaleidescape command response: %s", decoded_response)
                responses[command] = _parse_response_message(decoded_response)
            return responses
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()

    async def async_query_playback_state(self) -> dict[str, str | int | None]:
        responses = await self.async_send_requests(
            [
                "GET_PLAY_STATUS",
                "GET_MOVIE_LOCATION",
                "GET_VIDEO_MODE",
                "GET_VIDEO_COLOR",
                "GET_SCREEN_MASK",
                "GET_CINEMASCAPE_MODE",
                "GET_CINEMASCAPE_MASK",
                "GET_SYSTEM_READINESS_STATE",
                "GET_DEVICE_POWER_STATE",
                "GET_UI_STATE",
            ]
        )

        state: dict[str, str | int | float | None] = {
            "media_location": None,
            "play_status": None,
            "play_speed": None,
            "title_length": None,
            "title_location": None,
            "chapter_length": None,
            "chapter_location": None,
            "video_mode": None,
            "video_color_eotf": None,
            "video_color_space": None,
            "video_color_depth": None,
            "video_color_sampling": None,
            "screen_mask_ratio": None,
            "screen_mask_top_trim_rel": None,
            "screen_mask_bottom_trim_rel": None,
            "screen_mask_conservative_ratio": None,
            "screen_mask_top_mask_abs": None,
            "screen_mask_bottom_mask_abs": None,
            "cinemascape_mode": None,
            "cinemascape_mask": None,
            "system_readiness_state": None,
            "power_state": None,
            "ui_screen": None,
            "ui_popup": None,
            "ui_dialog": None,
        }

        play_status_response = responses.get("GET_PLAY_STATUS")
        movie_location_response = responses.get("GET_MOVIE_LOCATION")
        video_mode_response = responses.get("GET_VIDEO_MODE")
        video_color_response = responses.get("GET_VIDEO_COLOR")
        screen_mask_response = responses.get("GET_SCREEN_MASK")
        cinemascape_mode_response = responses.get("GET_CINEMASCAPE_MODE")
        cinemascape_mask_response = responses.get("GET_CINEMASCAPE_MASK")
        system_readiness_response = responses.get("GET_SYSTEM_READINESS_STATE")
        device_power_response = responses.get("GET_DEVICE_POWER_STATE")
        ui_state_response = responses.get("GET_UI_STATE")

        if (
            play_status_response
            and play_status_response.status == 0
            and play_status_response.name == "PLAY_STATUS"
            and len(play_status_response.fields) >= 8
        ):
            state["play_status"] = _decode_index(play_status_response.fields[0], PLAY_STATUS_INDEX)
            state["play_speed"] = _parse_int(play_status_response.fields[1])
            state["title_length"] = _parse_int(play_status_response.fields[3])
            state["title_location"] = _parse_int(play_status_response.fields[4])
            state["chapter_length"] = _parse_int(play_status_response.fields[6])
            state["chapter_location"] = _parse_int(play_status_response.fields[7])

        if (
            movie_location_response
            and movie_location_response.status == 0
            and movie_location_response.name == "MOVIE_LOCATION"
            and movie_location_response.fields
        ):
            state["media_location"] = _decode_index(
                movie_location_response.fields[0], MOVIE_LOCATION_INDEX
            )

        if (
            video_mode_response
            and video_mode_response.status == 0
            and video_mode_response.name == "VIDEO_MODE"
            and len(video_mode_response.fields) >= 3
        ):
            state["video_mode"] = _decode_index(video_mode_response.fields[2], VIDEO_MODE_INDEX)

        if (
            video_color_response
            and video_color_response.status == 0
            and video_color_response.name == "VIDEO_COLOR"
            and len(video_color_response.fields) >= 4
        ):
            state["video_color_eotf"] = _decode_index(
                video_color_response.fields[0], VIDEO_COLOR_EOTF_INDEX
            )
            state["video_color_space"] = _decode_index(
                video_color_response.fields[1], VIDEO_COLOR_SPACE_INDEX
            )
            state["video_color_depth"] = _decode_index(
                video_color_response.fields[2], VIDEO_COLOR_DEPTH_INDEX
            )
            state["video_color_sampling"] = _decode_index(
                video_color_response.fields[3], VIDEO_COLOR_SAMPLING_INDEX
            )

        if (
            screen_mask_response
            and screen_mask_response.status == 0
            and screen_mask_response.name == "SCREEN_MASK"
            and len(screen_mask_response.fields) >= 6
        ):
            state["screen_mask_ratio"] = _decode_index(
                screen_mask_response.fields[0], SCREEN_MASK_RATIO_INDEX
            )
            state["screen_mask_top_trim_rel"] = (
                _parse_int(screen_mask_response.fields[1]) or 0
            ) / 10.0
            state["screen_mask_bottom_trim_rel"] = (
                _parse_int(screen_mask_response.fields[2]) or 0
            ) / 10.0
            state["screen_mask_conservative_ratio"] = _decode_index(
                screen_mask_response.fields[3], SCREEN_MASK_RATIO_INDEX
            )
            state["screen_mask_top_mask_abs"] = (
                _parse_int(screen_mask_response.fields[4]) or 0
            ) / 10.0
            state["screen_mask_bottom_mask_abs"] = (
                _parse_int(screen_mask_response.fields[5]) or 0
            ) / 10.0

        if (
            cinemascape_mode_response
            and cinemascape_mode_response.status == 0
            and cinemascape_mode_response.name == "CINEMASCAPE_MODE"
            and cinemascape_mode_response.fields
        ):
            state["cinemascape_mode"] = _decode_index(
                cinemascape_mode_response.fields[0], CINEMASCAPE_MODE_INDEX
            )

        if (
            cinemascape_mask_response
            and cinemascape_mask_response.status == 0
            and cinemascape_mask_response.name == "CINEMASCAPE_MASK"
            and cinemascape_mask_response.fields
        ):
            state["cinemascape_mask"] = _parse_int(cinemascape_mask_response.fields[0])

        if (
            system_readiness_response
            and system_readiness_response.status == 0
            and system_readiness_response.name == "SYSTEM_READINESS_STATE"
            and system_readiness_response.fields
        ):
            state["system_readiness_state"] = _decode_index(
                system_readiness_response.fields[0], SYSTEM_READINESS_INDEX
            )

        if (
            device_power_response
            and device_power_response.status == 0
            and device_power_response.name == "DEVICE_POWER_STATE"
            and device_power_response.fields
        ):
            state["power_state"] = _decode_index(device_power_response.fields[0], POWER_STATE_INDEX)

        if (
            ui_state_response
            and ui_state_response.status == 0
            and ui_state_response.name == "UI_STATE"
            and len(ui_state_response.fields) >= 3
        ):
            state["ui_screen"] = _decode_index(ui_state_response.fields[0], UI_SCREEN_INDEX)
            state["ui_popup"] = _decode_index(ui_state_response.fields[1], UI_POPUP_INDEX)
            state["ui_dialog"] = _decode_index(ui_state_response.fields[2], UI_DIALOG_INDEX)

        return state
