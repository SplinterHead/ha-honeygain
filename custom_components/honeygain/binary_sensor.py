"""Binary sensors for HoneyGain data."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneygainData
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Binary Sensor set up for HoneyGain."""
    honeygain_data: HoneygainData = hass.data[DOMAIN][entry.entry_id]
    devices: list[BinarySensorEntity] = [
        HoneygainDeviceBinarySensor(honeygain_data, device)
        for device in honeygain_data.devices
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


class HoneygainDeviceBinarySensor(BinarySensorEntity):
    """Binary sensor to track Honeygain device."""

    honeygain_data: HoneygainData
    device_data: dict

    def __init__(self, honeygain_data: HoneygainData, device_data: dict) -> None:
        self._honeygain_data = honeygain_data
        self._device_data = device_data
        self._attr_unique_id = self._generate_unique_id()
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.honeygain.com/profile",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._generate_device_id())},
            manufacturer="Honeygain",
            name=self._device_data.get("title") or self._device_data.get("model"),
        )

        self.entity_description = _generate_binary_sensor_description("Status")

    def _generate_device_id(self):
        return f"honeygain-{self._device_data.get("ip")}"

    def _generate_unique_id(self):
        return f"{self._generate_device_id()}-status"

    def update(self) -> None:
        """Update Sensor data."""
        self._honeygain_data.update()
        self._device_data = next(
            (
                dev
                for dev in self._honeygain_data.devices
                if dev["id"] == self._device_data.get("id")
            ),
            None,
        )

    @property
    def is_on(self) -> bool:
        return self._device_data.get("status") == "active"
