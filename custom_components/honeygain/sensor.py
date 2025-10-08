"""Sensors for HoneyGain data."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneygainData
from .const import DOMAIN
from .entities import DEVICE_SENSORS, HONEYGAIN_SENSORS, SensorValueEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor set up for HoneyGain."""
    honeygain_data: HoneygainData = hass.data[DOMAIN][entry.entry_id]
    # List of sensors for the Honeygain Account
    account_entities: list[SensorEntity] = [
        HoneygainAccountSensor(honeygain_data, sensor_description)
        for sensor_description in HONEYGAIN_SENSORS
    ]
    async_add_entities(account_entities)
    # List of sensors for each Honeygain device
    for device in honeygain_data.devices:
        device_entities: list[SensorEntity] = [
            HoneygainDeviceSensor(honeygain_data, device, sensor_description)
            for sensor_description in DEVICE_SENSORS
        ]
        async_add_entities(device_entities)


class HoneygainAccountSensor(SensorEntity):
    """Sensor to track Honeygain Account data."""

    honeygain_data: HoneygainData
    entity_description: SensorValueEntityDescription

    def __init__(
        self,
        honeygain_data: HoneygainData,
        sensor_description: SensorValueEntityDescription,
    ) -> None:
        """Create Sensor for displaying Honeygain account details."""
        self._honeygain_data = honeygain_data
        self.entity_description = sensor_description
        self._attr_unique_id = self._generate_unique_id()
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.honeygain.com/profile",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._generate_account_id())},
            manufacturer="Honeygain",
            name="Account",
        )

    def _generate_account_id(self):
        return f"{DOMAIN}-{self._honeygain_data.user['referral_code']}"

    def _generate_unique_id(self):
        return f"{self._generate_account_id()}-{self.entity_description.key}"

    def update(self) -> None:
        """Update Sensor data."""
        self._honeygain_data.update()
        self._attr_native_value = self.entity_description.value(self._honeygain_data)


class HoneygainDeviceSensor(SensorEntity):
    """Sensor to track Honeygain Device data."""

    honeygain_data: HoneygainData
    device_data = dict
    entity_description = SensorValueEntityDescription

    def __init__(
        self,
        honeygain_data: HoneygainData,
        device_data: dict,
        sensor_description: SensorValueEntityDescription,
    ) -> None:
        """Create Sensor for displaying Honeygain device details."""
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
        self._attr_native_value = self.entity_description.value(self._device_data)

    def _generate_device_id(self):
        return f"{DOMAIN}-{self._device_data.get("ip")}"

    def _generate_unique_id(self):
        return f"{self._generate_device_id()}-{self.entity_description.key}"

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
        self._attr_native_value = self.entity_description.value(self._device_data)
