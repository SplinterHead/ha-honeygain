"""The Honeygain integration."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
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
    # Minor version 2: device ids no longer built from the IP
    if entry.minor_version < 2:
        await _migrate_ip_identifiers(hass, entry, hg_account.devices)
        hass.config_entries.async_update_entry(entry, minor_version=2)

    # Set up all platforms for this device/entry.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Allow removing devices that Honeygain no longer reports."""
    hg_account: HoneygainData = hass.data[DOMAIN][entry.entry_id]
    current = {f"{DOMAIN}-{dev.get('id')}" for dev in hg_account.devices}
    current.add(f"{DOMAIN}-{hg_account.user.get('referral_code')}")
    return not any(
        domain == DOMAIN and ident in current
        for domain, ident in device_entry.identifiers
    )


async def _migrate_ip_identifiers(
    hass: HomeAssistant, entry: ConfigEntry, devices: list[dict]
) -> None:
    """Move devices and entities from the old IP based ids to the device id."""
    devices = [dev for dev in devices if dev.get("id")]
    ip_count = Counter(dev.get("ip") for dev in devices)
    # An IP shared by several clients can't tell which one the old entries belong to
    new_ids = {
        f"{DOMAIN}-{dev.get('ip')}": f"{DOMAIN}-{dev['id']}"
        for dev in devices
        if ip_count[dev.get("ip")] == 1
    }

    dev_reg = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        for domain, ident in device.identifiers:
            if domain == DOMAIN and ident in new_ids:
                dev_reg.async_update_device(
                    device.id, new_identifiers={(DOMAIN, new_ids[ident])}
                )

    def _new_unique_id(entity: er.RegistryEntry) -> dict | None:
        old_id, _, key = entity.unique_id.rpartition("-")
        if old_id in new_ids:
            return {"new_unique_id": f"{new_ids[old_id]}-{key}"}
        return None

    await er.async_migrate_entries(hass, entry.entry_id, _new_unique_id)


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
