import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from eg4_inverter_api import EG4InverterAPI
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
)

_LOGGER = logging.getLogger(__name__)


class EG4DataCoordinator(DataUpdateCoordinator):
    """Manages login and fetching data from EG4 Inverter API."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize the coordinator with config entry data."""
        self.hass = hass
        self.entry = entry
        session = async_get_clientsession(hass)

        # Extract config fields from entry.data
        username = entry.data[CONF_USERNAME]
        password = entry.data[CONF_PASSWORD]
        base_url = entry.data[CONF_BASE_URL]
        self.serial_number = entry.data.get(CONF_SERIAL_NUMBER, 30)
        self.ignore_ssl = entry.data.get(CONF_IGNORE_SSL, False)

        # Instantiate the EG4InverterAPI client
        self.api = EG4InverterAPI(
            username, password, base_url=base_url, session=session
        )

        # We'll track if we've done the initial login
        self._logged_in = False
        self._update_interval = timedelta(
            seconds=entry.data.get(
                CONF_RUNTIME_INTERVAL_SECONDS, DEFAULT_RUNTIME_INTERVAL_SECONDS
            )
        )
        self._settings_interval = timedelta(
            seconds=entry.data.get(
                CONF_SETTINGS_INTERVAL_SECONDS, DEFAULT_SETTINGS_INTERVAL_SECONDS
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            name="EG4DataCoordinator",
            update_interval=self._update_interval,
        )
        # Track the last time we fetched settings
        self._last_settings_fetch = None

        # Cache “old” settings so we don’t lose them in partial updates
        self._cached_settings = None
        self._cached_runtime = None
        self._cached_energy = None
        self._cached_battery = None
        self._using_cache = False

    async def _async_update_data(self):
        """Fetch data from the EG4 Inverter API, called by HA every 'update_interval' seconds."""
        # Perform login and inverter selection only once
        if not self._logged_in:
            await self._async_login_and_select_inverter()
            self._logged_in = True

        # Always fetch runtime data
        self._using_cache = False
        try:
            _LOGGER.debug("Getting Inverter Data")
            inverter_info = self.api.get_selected_inverter()
            _LOGGER.debug(f"Got Inverter Data: {inverter_info}")

            _LOGGER.debug("Getting Runtime Data")
            try:
                runtime_data = await self.api.get_inverter_runtime_async()
                if runtime_data != None:
                    self._cached_runtime = runtime_data
                else:
                    self._using_cache = True               
                    raise Exception("Use Cache")
            except:
                runtime_data = self._cached_runtime
            _LOGGER.debug(f"Got Runtime Data: {runtime_data}")

            _LOGGER.debug("Getting battery Data")
            try:
                battery_data = await self.api.get_inverter_battery_async()
                if battery_data != None:
                    self._cached_battery = battery_data
                else:
                    self._using_cache = True               
                    raise Exception("Use Cache")
            except:
                battery_data = self._cached_battery
            
            _LOGGER.debug(f"Got battery Data: {battery_data}")

            _LOGGER.debug("Getting energy Data")
            try:
                energy_data = await self.api.get_inverter_energy_async()
                if energy_data != None:
                    self._cached_energy = energy_data
                else:
                    self._using_cache = True               
                    raise Exception("Use Cache")
            except:
                energy_data = self._cached_energy
            _LOGGER.debug(f"Got energy Data: {energy_data}")
            if energy_data is None:
                raise Exception
        except Exception as err:
            raise UpdateFailed(f"Error fetching runtime data: {err}") from err

        # Conditionally fetch settings if enough time has passed
        now = dt_util.utcnow()
        need_settings = False

        if (
            self._last_settings_fetch is None
            or (now - self._last_settings_fetch) >= self._settings_interval
        ):
            need_settings = True

        if need_settings:
            try:
                settings_data = await self.api.read_settings_async()
                self._cached_settings = settings_data
                self._last_settings_fetch = now
            except Exception as err:
                _LOGGER.warning("Failed to update settings: %s", err)
                # We don't raise UpdateFailed here because we at least want the
                # runtime data to be updated. We'll just keep old settings.
        else:
            settings_data = self._cached_settings

        # Return combined data
        return {
            "inverter": inverter_info,
            "runtime": runtime_data,
            "battery": battery_data,
            "energy": energy_data,
            "settings": settings_data,
        }

    async def _async_login_and_select_inverter(self):
        """Login to the EG4 API and set the inverter serial number."""
        _LOGGER.debug("Logging into EG4 and setting inverter serial")
        await self.api.login(ignore_ssl=self.ignore_ssl)
        self.api.set_selected_inverter(serialNum=self.serial_number)
        _LOGGER.debug(
            "Successfully logged in and selected inverter %s", self.serial_number
        )

    async def force_refresh_settings(self):
        """Public method to immediately refresh settings (e.g., after a write)."""
        try:
            settings_data = await self.api.read_settings_async()
            self._cached_settings = settings_data
            self._last_settings_fetch = dt_util.utcnow()
        except Exception as err:
            _LOGGER.error("Error force-refreshing settings: %s", err)
