"""Sensors for HoneyGain data."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_DOLLAR, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneygainData
from .const import DOMAIN


@dataclass
class SensorValueEntityDescription(SensorEntityDescription):
    """Class describing Honeygain sensor entities."""

    value: Callable = lambda x: x


HONEYGAIN_SENSORS: list[SensorValueEntityDescription] = [
    # Account Balance
    SensorValueEntityDescription(
        key="account_balance",
        name="Account balance",
        icon="mdi:hand-coin",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=CURRENCY_DOLLAR,
        value=lambda x: f'{x.balances.get("payout").get("usd_cents") / 100:.2f}',
    ),
    # Active Devices
    SensorValueEntityDescription(
        key="active_devices",
        name="Active device count",
        icon="mdi:server-network",
        value=lambda x: x.user.get("active_devices_count"),
    ),
    # Daily Stats
    SensorValueEntityDescription(
        key="today_earnings",
        name="Today's earnings",
        icon="mdi:calendar-today",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=CURRENCY_DOLLAR,
        value=lambda x: f'{x.balances.get("realtime").get("usd_cents") / 100:.2f}',
    ),
    SensorValueEntityDescription(
        key="today_credits",
        name="Today's credits",
        icon="mdi:calendar-today",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats.get("gathering").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_credits_jt",
        name="Today's JMPT credits",
        icon="mdi:calendar-today",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats_jt.get("gathering").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_total_credits",
        name="Today's total credits",
        icon="mdi:calendar-today",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats.get("total").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_total_credits_jt",
        name="Today's total JMPT credits",
        icon="mdi:calendar-today",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats_jt.get("total").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_bandwidth",
        name="Today's shared bandwidth",
        icon="mdi:upload",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        value=lambda x: f'{round(x.today_stats.get("gathering").get("bytes"), -4) / 1000000}',
    ),
    SensorValueEntityDescription(
        key="today_referral_credits",
        name="Today's referral credits",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats.get("referral").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_referral_credits_jt",
        name="Today's JMPT referral credits",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats_jt.get("referral").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_lucky_pot_credits",
        name="Today's Lucky Pot credits",
        icon="mdi:gift-open",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats.get("winning").get("credits"),
    ),
    SensorValueEntityDescription(
        key="today_lucky_pot_credits_jt",
        name="Today's JMPT Lucky Pot credits",
        icon="mdi:gift-open",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.today_stats_jt.get("winning").get("credits"),
    ),
]

DEVICE_SENSORS: list[SensorValueEntityDescription] = [
    SensorValueEntityDescription(
        key="ip_address",
        name="IP address",
        icon="mdi:ip-network",
        value=lambda x: x.get("ip"),
    ),
    SensorValueEntityDescription(
        key="total_traffic",
        name="Total traffic",
        icon="mdi:upload",
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        value=lambda x: f'{round(x.get("stats").get("total_traffic"), -4) / 1000000}',
    ),
    SensorValueEntityDescription(
        key="total_credits",
        name="Total credits",
        icon="mdi:hand-coin",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.get("stats").get("total_credits"),
    ),
    SensorValueEntityDescription(
        key="last_active",
        name="Last active",
        icon="mdi:web-clock",
        value=lambda x: x.get("last_active_time"),
    ),
]


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
        self.entity_description = sensor_description
        self._honeygain_data = honeygain_data
        self._attr_unique_id = self._generate_unique_id()
        self._attr_native_value = sensor_description.value(honeygain_data)
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.honeygain.com/profile",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._honeygain_data.user.get("referral_code"))},
            manufacturer="Honeygain",
            name="Account",
        )

    def _generate_unique_id(self):
        return f"honeygain-{self._honeygain_data.user['referral_code']}-{self.entity_description.key}"

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
        self.entity_description = sensor_description
        self._honeygain_data = honeygain_data
        self._device_data = device_data
        self._attr_unique_id = self._generate_unique_id()
        self._attr_device_info = DeviceInfo(
            configuration_url="https://dashboard.honeygain.com/profile",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._generate_device_id())},
            manufacturer="Honeygain",
            name=self._device_data.get("title") or self._device_data.get("model"),
        )
        self._attr_native_value = self.entity_description.value(self._device_data)

    def _generate_device_id(self):
        return f"honeygain-{self._device_data.get("ip")}"

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
