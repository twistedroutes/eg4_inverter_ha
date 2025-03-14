import logging
from typing import Any, Dict
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .coordinator import EG4DataCoordinator
from .const import DOMAIN
from .definitions import (
    PER_BATTERY_DEFS,
    BATTERY_SUMMARY_SENSORS,
    ENERGY_SENSORS,
    RUNTIME_SENSORS,
)

_LOGGER = logging.getLogger(__name__)


# -------------------------------------------------------------------------
#   SETUP: CREATE ENTITIES FROM DEFINITIONS
# -------------------------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EG4 inverter binary sensors from a config entry."""
    coordinator: EG4DataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # BATTERY SUMMARY BINARY SENSORS
    for sensor_def in BATTERY_SUMMARY_SENSORS:
        if sensor_def.get("type", "") == "binary_sensor":
            entities.append(
                EG4InverterBinarySensor(coordinator, entry, sensor_def, "battery")
            )

    # ENERGY BINARY SENSORS
    for sensor_def in ENERGY_SENSORS:
        if sensor_def.get("type", "") == "binary_sensor":
            entities.append(
                EG4InverterBinarySensor(coordinator, entry, sensor_def, "energy")
            )

    # RUNTIME BINARY SENSORS
    for sensor_def in RUNTIME_SENSORS:
        if sensor_def.get("type", "") == "binary_sensor":
            entities.append(
                EG4InverterBinarySensor(coordinator, entry, sensor_def, "runtime")
            )

    # PER-BATTERY BINARY SENSORS
    battery_data = coordinator.data.get("battery", {})
    battery_units = battery_data.battery_units or []
    for binfo in battery_units:
        for subdef in PER_BATTERY_DEFS:
            subdef = subdef.copy()
            if subdef["type"] != "binary_sensor":
                continue
            name_template = subdef.get("name", "")
            dynamic_name = name_template.format(binfo=binfo)
            if name_template != dynamic_name:
                subdef["name"] = dynamic_name
            entities.append(
                EG4PerBatteryBinarySensor(coordinator, entry, binfo, subdef)
            )

    async_add_entities(entities)


# -------------------------------------------------------------------------
# BASE BINARY SENSOR CLASSES
# -------------------------------------------------------------------------
class EG4BaseBinarySensor(BinarySensorEntity):
    """Common base for EG4 binary sensors that integrates with the coordinator."""

    def __init__(self, coordinator, entry):
        """Initialize the base binary sensor."""
        self._coordinator = coordinator
        self._entry = entry

    @property
    def should_poll(self) -> bool:
        """No polling, coordinator notifies us."""
        return False

    async def async_added_to_hass(self):
        """When entity is added to HA, subscribe to coordinator updates."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        """Return true if coordinator was able to update successfully."""
        return self._coordinator.last_update_success

    @property
    def device_info(self):
        """Put all sensors under one device in the UI."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "EG4 Inverter",
            "manufacturer": "EG4",
        }


class EG4InverterBinarySensor(EG4BaseBinarySensor):
    """A binary sensor for defined data points in battery, runtime, or energy."""

    def __init__(self, coordinator, entry, sensor_def: Dict[str, Any], parent_key: str):
        super().__init__(coordinator, entry)
        self._sensor_def = sensor_def
        self._parent_key = parent_key

        self._attr_unique_id = f"{entry.entry_id}_{parent_key}_{sensor_def['key']}"
        self._attr_name = sensor_def.get("name", sensor_def["key"])
        self._attr_device_class = sensor_def.get("device_class")

    @property
    def is_on(self) -> bool:
        data = self._coordinator.data.get(self._parent_key, {})
        try:
            raw_value = getattr(data, self._sensor_def["key"])
        except Exception as e:
            raw_value = data.get(self._sensor_def["key"], False)

        calc_func = self._sensor_def.get("calc")
        if calc_func:
            return calc_func(data)
        return bool(raw_value)

class EG4PerBatteryBinarySensor(EG4BaseBinarySensor):
    """A binary sensor for each battery in battery_units."""

    def __init__(
        self,
        coordinator,
        entry,
        battery_info: Dict[str, Any],
        sensor_def: Dict[str, Any],
    ):
        super().__init__(coordinator, entry)
        self._battery_info = battery_info
        self._sensor_def = sensor_def

        battery_idx = battery_info.batIndex or "Unknown"
        key = sensor_def["key"]
        self._attr_unique_id = f"{entry.entry_id}_battery_{battery_idx}_{key}"
        self._attr_name = sensor_def.get("name", f"{battery_idx} {key}")
        self._attr_device_class = sensor_def.get("device_class")

    @property
    def is_on(self) -> bool:
        try:
            raw_value = getattr(self._battery_info, self._sensor_def["key"], None)
        except Exception as e:
            raw_value = self._battery_info.get(self._sensor_def["key"])

        calc_func = self._sensor_def.get("calc")
        if calc_func:
            return calc_func(self._battery_info)
        return bool(raw_value)
