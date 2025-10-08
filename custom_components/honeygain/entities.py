from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.const import CURRENCY_DOLLAR, UnitOfInformation


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
        key="client_manufacturer",
        name="Client manufacturer",
        icon="mdi:account-wrench",
        value=lambda x: x.get("manufacturer"),
    ),
    SensorValueEntityDescription(
        key="client_platform",
        name="Client platform",
        icon="mdi:desktop-classic",
        value=lambda x: x.get("platform"),
    ),
    SensorValueEntityDescription(
        key="client_version",
        name="Client version",
        icon="mdi:check-decagram",
        value=lambda x: x.get("version"),
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
        key="streaming_seconds",
        name="Streaming seconds",
        icon="mdi:home-clock",
        state_class=SensorStateClass.TOTAL,
        value=lambda x: x.get("stats").get("streaming_seconds"),
    ),
    SensorValueEntityDescription(
        key="last_active",
        name="Last active",
        icon="mdi:web-clock",
        value=lambda x: x.get("last_active_time"),
    ),
]


@dataclass
class BinarySensorValueEntityDescription(BinarySensorEntityDescription):
    """Class describing Honeygain binary sensor entities."""

    value: Callable = lambda x: x


DEVICE_BINARY_SENSORS: list[BinarySensorValueEntityDescription] = [
    BinarySensorValueEntityDescription(
        key="status",
        name="Status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value=lambda x: x.get("status") == "active",
    ),
    BinarySensorValueEntityDescription(
        key="streaming", name="Streaming", value=lambda x: x.get("streaming_enabled")
    ),
]
