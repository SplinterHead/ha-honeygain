"""The Honeygain integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import Throttle
from pyHoneygain import HoneyGain
from requests import RequestException

from .const import DOMAIN, LOGGER, UPDATE_INTERVAL_MINS

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.BUTTON]

UPDATE_INTERVAL = timedelta(minutes=UPDATE_INTERVAL_MINS)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Honeygain from a config entry."""
    try:
        hg_account = await validate_authentication(hass, entry)
    # pyHoneygain raises KeyError when the login answer has no token
    except (RequestException, KeyError) as exc:
        raise ConfigEntryNotReady(
            "Cannot log in to Honeygain, check the credentials if this persists"
        ) from exc
    await hass.async_add_executor_job(hg_account.update)
    if not hg_account.available:
        raise ConfigEntryNotReady("Cannot fetch data from Honeygain")
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
        # None until the first update, so a failure at startup is logged too
        self.available: bool | None = None

    @Throttle(UPDATE_INTERVAL)
    def update(self) -> None:
        """Pull the latest data."""
        try:
            # Use the V1 endpoint to pull basic details
            self.honeygain.set_api_version(version="/v1", reload=True)
            data = {
                "balances": self.honeygain.balances(),
                "stats": self.honeygain.stats(),
                "stats_jt": self.honeygain.stats_jt(),
                "today_stats": self.honeygain.stats_today(),
                "today_stats_jt": self.honeygain.stats_today_jt(),
                "user": self.honeygain.me(),
            }

            # Use the V2 endpoint to pull advanced details
            self.honeygain.set_api_version(version="/v2", reload=True)
            data["devices"] = self.honeygain.devices()
        # pyHoneygain raises requests errors, its own errors or plain parsing
        # errors on unexpected answers: any of them is a failed update
        except Exception as exc:  # pylint: disable=broad-except
            failed = repr(exc)
        else:
            # pyHoneygain returns False on HTTP errors, None or {} on a missing payload
            failed = ", ".join(k for k, v in data.items() if v in (False, None, {}))
        finally:
            # Reset back to the V1 endpoint
            self.honeygain.set_api_version(version="/v1", reload=True)

        # Keep the last good data and log once per outage, not on every entity
        if failed:
            if self.available is not False:
                LOGGER.warning("Honeygain update failed (%s)", failed)
            self.available = False
            return
        if self.available is False:
            LOGGER.info("Honeygain update succeeded")
        for key, value in data.items():
            setattr(self, key, value)
        self.available = True

    def open_daily_pot(self) -> None:
        """Open the daily pot if it's available."""
        try:
            self.honeygain.open_honeypot()
        except Exception as exc:
            LOGGER.error("Failed to open daily pot: %s", exc)
            raise Exception from exc
