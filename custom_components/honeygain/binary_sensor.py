"""Binary sensors for HoneyGain data."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneygainData
from .const import DOMAIN
from .entities import DEVICE_BINARY_SENSORS, BinarySensorValueEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Binary Sensor set up for HoneyGain."""
    honeygain_data: HoneygainData = hass.data[DOMAIN][entry.entry_id]
    for device in honeygain_data.devices:
        device_entities: list[BinarySensorEntity] = [
            HoneygainDeviceBinarySensor(honeygain_data, device, sensor_description)
            for sensor_description in DEVICE_BINARY_SENSORS
        ]
        async_add_entities(device_entities)


class HoneygainDeviceBinarySensor(BinarySensorEntity):
    """Binary sensor to track Honeygain device."""

    honeygain_data: HoneygainData
    device_data: dict
    sensor_description: BinarySensorValueEntityDescription

    def __init__(
        self,
        honeygain_data: HoneygainData,
        device_data: dict,
        sensor_description: BinarySensorValueEntityDescription,
    ) -> None:
        self._honeygain_data = honeygain_data
        self._device_data = device_data
        self.entity_description = sensor_description
        self._attr_unique_id = self._generate_unique_id()
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.honeygain.com/profile",
            identifiers={(DOMAIN, self._generate_device_id())},
            manufacturer="Honeygain",
            name=self._device_data.get("title") or self._device_data.get("model"),
        )

    def _generate_device_id(self):
        return f"{DOMAIN}-{self._device_data.get("ip")}"

    def _generate_unique_id(self):
        return f"{self._generate_device_id()}-{self.entity_description.key}"

    def update(self) -> None:
        """Update Sensor data."""
        self._honeygain_data.update()
        device_data = self._honeygain_data.get_device(self._device_data.get("id"))
        # Removed from the account: unavailable, the old data keeps the id to look up
        self._attr_available = device_data is not None
        if device_data is not None:
            self._device_data = device_data

    @property
    def is_on(self) -> bool:
        return self.entity_description.value(self._device_data)
