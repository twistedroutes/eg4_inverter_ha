import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from eg4_inverter_api import EG4InverterAPI
from eg4_inverter_api.exceptions import EG4APIError, EG4AuthError
from eg4_inverter_api.models import (
    APIResponse,
    BatteryData,
    BatteryUnit,
    EnergyData,
    Inverter,
    RuntimeData,
    InverterParameters,
)
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_BASE_URL,
    CONF_SERIAL_NUMBER,
    CONF_IGNORE_SSL,
    CONF_RUNTIME_INTERVAL_SECONDS,
    CONF_SETTINGS_INTERVAL_SECONDS,
    DEFAULT_RUNTIME_INTERVAL_SECONDS,
    DEFAULT_SETTINGS_INTERVAL_SECONDS,
    DEFAULT_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME, default=""): str,
        vol.Required(CONF_PASSWORD, default=""): str,
        vol.Required(CONF_SERIAL_NUMBER, default=""): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        vol.Optional(CONF_IGNORE_SSL, default=False): bool,
        vol.Optional(
            CONF_RUNTIME_INTERVAL_SECONDS, default=DEFAULT_RUNTIME_INTERVAL_SECONDS
        ): int,
        vol.Optional(
            CONF_SETTINGS_INTERVAL_SECONDS, default=DEFAULT_SETTINGS_INTERVAL_SECONDS
        ): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )
    session = async_get_clientsession(hass)
    api = EG4InverterAPI(
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        base_url=data[CONF_BASE_URL],
        session=session,
    )
    try:
        await api.login(ignore_ssl=data[CONF_IGNORE_SSL])
        inverters = api.get_inverters()
        _LOGGER.info(f"EG4 Inverter Login: {inverters}")

        if data.get(CONF_SERIAL_NUMBER):
            selected_inverter = [
                x for x in inverters if x.serialNum == data.get(CONF_SERIAL_NUMBER)
            ]
            if len(selected_inverter) > 0:
                selected_inverter = selected_inverter[0]
                _LOGGER.info(f"EG4 Inverter Selected: {selected_inverter}")
            else:
                selected_inverter = None

            api.set_selected_inverter(serialNum=data[CONF_SERIAL_NUMBER])
        else:
            _LOGGER.warning(f"DEFAULT EG4 Inverter at index 0 Selected: {inverters[0]}")
            api.set_selected_inverter(inverterIndex=0)
    except EG4AuthError as err:
        raise InvalidAuth from err
    except EG4APIError as err:
        raise CannotConnect from err
    return {"title": f"EG4 Inverter Integration - {data[CONF_BASE_URL]}"}


class EG4InverterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EG4 Inverter Integration."""

    VERSION = 1
    _input_data: dict[str, Any]

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        # Remove this method and the ExampleOptionsFlowHandler class
        # if you do not want any options for your integration.
        return OptionsFlowHandler(config_entry)
        # return ExampleOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        _LOGGER.debug("EG4 Inverter async_step_user() called")
        """Handle the initial step."""
        # Called when you initiate adding an integration via the UI
        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                # Validate that the setup data is valid and if not handle errors.
                # The errors["base"] values match the values in your strings.json and translation files.
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so create a unique id for this instance of your integration
                # and create the config entry.
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show initial form.
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add reconfigure step to allow to reconfigure a config entry."""
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            try:
                user_input[CONF_USERNAME] = config_entry.data[CONF_USERNAME]
                user_input[CONF_PASSWORD] = config_entry.data[CONF_PASSWORD]
                user_input[CONF_SERIAL_NUMBER] = config_entry.data[CONF_SERIAL_NUMBER]
                user_input[CONF_IGNORE_SSL] = config_entry.data[CONF_IGNORE_SSL]
                user_input[CONF_BASE_URL] = config_entry.data[CONF_BASE_URL]
                user_input[CONF_RUNTIME_INTERVAL_SECONDS] = config_entry.data[
                    CONF_RUNTIME_INTERVAL_SECONDS
                ]
                user_input[CONF_SETTINGS_INTERVAL_SECONDS] = config_entry.data[
                    CONF_SETTINGS_INTERVAL_SECONDS
                ]
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={**config_entry.data, **user_input},
                    reason="reconfigure_successful",
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class OptionsFlowHandler(OptionsFlow):
    """Handles the options flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            options = self._entry.options | user_input
            return self.async_create_entry(title="", data=options)

        # It is recommended to prepopulate options fields with default values if available.
        # These will be the same default values you use on your coordinator for setting variable values
        # if the option has not been set.
        # data_schema = vol.Schema(
        #    {
        #        vol.Optional(
        #            CONF_BASE_URL, default="https://monitor.eg4electronics.com"
        #        ): str,
        #    }
        # )

        # return self.async_show_form(step_id="init", data_schema=data_schema)
        return self.async_show_form(step_id="init", data_schema=STEP_USER_DATA_SCHEMA)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


#############

"""
class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(step_id="init")
"""
