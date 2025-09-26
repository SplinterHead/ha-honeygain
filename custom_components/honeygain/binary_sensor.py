"""Binary sensors for HoneyGain data."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneygainData
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Binary Sensor set up for HoneyGain."""
    honeygain_data: HoneygainData = hass.data[DOMAIN][entry.entry_id]
    devices: list[BinarySensorEntity] = [
        HoneygainDeviceBinarySensor(device) for device in honeygain_data.devices
    ]
    async_add_entities(devices)

    for device in honeygain_data.devices:
        _LOGGER.error(device)


def _generate_binary_sensor_description(device_name: str):
    return BinarySensorEntityDescription(
        key="status",
        name=device_name,
        icon="mdi:cloud-upload",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    )


def _generate_unique_id(device_data):
    return f"honeygain-{device_data.get('ip')}-status"


class HoneygainDeviceBinarySensor(BinarySensorEntity):
    """Binary sensor to track Honeygain device."""

    device_data: dict

    def __init__(self, device_data: dict) -> None:
        self._device_data = device_data
        self._attr_unique_id = _generate_unique_id(device_data)
        self._attr_has_entity_name = True

        self.entity_description = _generate_binary_sensor_description(
            f"{self._device_data.get("title") or self._device_data.get("model") or self._attr_unique_id} Status"
        )

    @property
    def is_on(self) -> bool:
        return self._device_data.get("status") == "active"
