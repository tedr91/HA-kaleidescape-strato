from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_TIMEOUT
from homeassistant.data_entry_flow import FlowResult

from .api import KaleidescapeClient
from .const import DEFAULT_NAME, DEFAULT_PORT, DEFAULT_TIMEOUT, DOMAIN


class KaleidescapeStratoConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

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
