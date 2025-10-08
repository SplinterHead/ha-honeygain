"""The Honeygain integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle
from pyHoneygain import HoneyGain

from .config_flow import CannotConnect, InvalidAuth
from .const import DOMAIN, LOGGER, UPDATE_INTERVAL_MINS

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.BUTTON]

UPDATE_INTERVAL = timedelta(minutes=UPDATE_INTERVAL_MINS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Honeygain from a config entry."""
    hg_account = await validate_authentication(hass, entry)
    await hass.async_add_executor_job(hg_account.update)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hg_account

    # Set up all platforms for this device/entry.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def validate_authentication(
    hass: HomeAssistant, entry: ConfigEntry
) -> HoneygainData:
    """Create and authenticate an API instance."""
    honeygain = HoneyGain()
    await hass.async_add_executor_job(
        honeygain.login, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD]
    )
    hg_account = HoneygainData(honeygain)
    return hg_account


# pylint: disable=too-few-public-methods
class HoneygainData:
    """Poll for new data."""

    def __init__(self, honeygain: HoneyGain) -> None:
        """Create instance ready for data updates."""
        self.honeygain: HoneyGain = honeygain
        self.balances: dict = {}
        self.devices: dict = {}
        self.stats: dict = {}
        self.stats_jt: dict = {}
        self.today_stats: dict = {}
        self.today_stats_jt: dict = {}
        self.user: dict = {}

    @Throttle(UPDATE_INTERVAL)
    def update(self) -> None:
        """Pull the latest data."""
        try:
            # Use the V1 endpoint to pull basic details
            self.honeygain.set_api_version(version="/v1", reload=True)
            self.balances = self.honeygain.balances()
            self.stats = self.honeygain.stats()
            self.stats_jt = self.honeygain.stats_jt()
            self.today_stats = self.honeygain.stats_today()
            self.today_stats_jt = self.honeygain.stats_today_jt()
            self.user = self.honeygain.me()

            # Use the V2 endpoint to pull advanced details
            self.honeygain.set_api_version(version="/v2", reload=True)
            self.devices = self.honeygain.devices()
            LOGGER.error(self.devices)

            # Reset back to the V1 endpoint
            self.honeygain.set_api_version(version="/v1", reload=True)

        except CannotConnect:
            LOGGER.warning("Failed to connect to Honeygain for update")
        except InvalidAuth:
            LOGGER.warning("Failed to authenticate with Honeygain for update")

    def open_daily_pot(self) -> None:
        """Open the daily pot if it's available."""
        try:
            self.honeygain.open_honeypot()
        except Exception as exc:
            LOGGER.error("Failed to open daily pot: %s", exc)
            raise Exception from exc
