from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.service_info.ssdp import (
    ATTR_UPNP_FRIENDLY_NAME,
    ATTR_UPNP_SERIAL,
    SsdpServiceInfo,
)

from .api import KaleidescapeClient
from .const import (
    CONF_DEBUG_COMMANDS,
    DEFAULT_DEBUG_COMMANDS,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DOMAIN,
)


class KaleidescapeStratoConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    _discovered_host: str | None = None
    _discovered_name: str = DEFAULT_NAME

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return KaleidescapeStratoOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()

            client = KaleidescapeClient(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                timeout=user_input[CONF_TIMEOUT],
            )

            if await client.async_can_connect():
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

            errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.Coerce(float),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_ssdp(self, discovery_info: SsdpServiceInfo) -> FlowResult:
        """Handle SSDP discovery for Kaleidescape players."""
        if discovery_info.ssdp_location is None:
            return self.async_abort(reason="cannot_connect")

        discovered_host = urlparse(discovery_info.ssdp_location).hostname
        if discovered_host is None:
            return self.async_abort(reason="cannot_connect")

        serial_number = str(discovery_info.upnp.get(ATTR_UPNP_SERIAL, discovered_host))

        await self.async_set_unique_id(serial_number, raise_on_progress=False)
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovered_host})

        client = KaleidescapeClient(
            host=discovered_host,
            port=DEFAULT_PORT,
            timeout=DEFAULT_TIMEOUT,
        )
        if not await client.async_can_connect():
            return self.async_abort(reason="cannot_connect")

        self._discovered_host = discovered_host
        self._discovered_name = str(
            discovery_info.upnp.get(ATTR_UPNP_FRIENDLY_NAME, DEFAULT_NAME)
        )
        self.context.update({"title_placeholders": {"name": self._discovered_name}})
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Confirm setup of a discovered Kaleidescape player."""
        if self._discovered_host is None:
            return self.async_abort(reason="cannot_connect")

        if user_input is None:
            return self.async_show_form(
                step_id="discovery_confirm",
                description_placeholders={"name": self._discovered_name},
                errors={},
            )

        return self.async_create_entry(
            title=self._discovered_name,
            data={
                CONF_NAME: self._discovered_name,
                CONF_HOST: self._discovered_host,
                CONF_PORT: DEFAULT_PORT,
                CONF_TIMEOUT: DEFAULT_TIMEOUT,
            },
        )


class KaleidescapeStratoOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEBUG_COMMANDS,
                    default=self._config_entry.options.get(
                        CONF_DEBUG_COMMANDS,
                        DEFAULT_DEBUG_COMMANDS,
                    ),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
