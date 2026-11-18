"""Config flow for Honeygain integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from pyHoneygain import HoneyGain
from requests.exceptions import JSONDecodeError

from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_EMAIL): str, vol.Required(CONF_PASSWORD): str}
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class HoneygainHub:  # pylint: disable=too-few-public-methods
    """Initialise and authenticate credentials."""

    honeygain: HoneyGain

    def __init__(self) -> None:
        """Initialize."""
        self.honeygain = HoneyGain()

    def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the API."""
        try:
            return self.honeygain.login(username, password)
        except JSONDecodeError as exc:
            LOGGER.error("Failed to connect to Honeygain for authentication")
            raise CannotConnect from exc
        except KeyError as exc:
            LOGGER.error("Failed to validate the credentials")
            raise InvalidAuth from exc


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = HoneygainHub()

    if not await hass.async_add_executor_job(
        hub.authenticate, data[CONF_EMAIL], data[CONF_PASSWORD]
    ):
        raise InvalidAuth


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Honeygain."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
            self._abort_if_unique_id_configured()
            if not (errors := await self._check(user_input)):
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Honeygain rejected the stored credentials."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask for the new password."""
        errors = {}
        if user_input is not None:
            entry = self._get_reauth_entry()
            if not (errors := await self._check({**entry.data, **user_input})):
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )

    async def _check(self, data: dict[str, Any]) -> dict[str, str]:
        """Return the form errors for these credentials, none if they work."""
        try:
            await validate_input(self.hass, data)
        except CannotConnect:
            LOGGER.exception("Failed to connect to Honeygain")
            return {"base": "cannot_connect"}
        except InvalidAuth:
            LOGGER.exception("Invalid Authentication")
            return {"base": "invalid_auth"}
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            return {"base": "unknown"}
        return {}
