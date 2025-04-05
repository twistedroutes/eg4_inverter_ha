import logging
from typing import Any, Dict
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfTime,
    UnitOfMass,
)
from .coordinator import EG4DataCoordinator
from .const import DOMAIN
from .definitions import (
    PER_BATTERY_DEFS,
    BATTERY_SUMMARY_SENSORS,
    ENERGY_SENSORS,
    RUNTIME_SENSORS,
    SETTING_SENSORS,
)

_LOGGER = logging.getLogger(__name__)


def parse_float(value: Any, scale: float = 1.0) -> float | None:
    """Helper to convert strings/numbers to float, applying a scale if needed."""
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value or value == "--":
                return None
        return float(value) * scale
    except (ValueError, TypeError):
        return None


# -------------------------------------------------------------------------
#   SETUP: CREATE ENTITIES FROM DEFINITIONS
#    We also show how to create multiple sensors for each battery in battery_units.
# -------------------------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EG4 inverter sensors from a config entry."""
    coordinator: EG4DataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # 4.1) ENERGY SENSORS
    for sensor_def in ENERGY_SENSORS:
        if sensor_def.get("type", "") == "sensor":
            entities.append(
                EG4InverterSensor(coordinator, entry, sensor_def, parent_key="energy")
            )

    # 4.2) RUNTIME SENSORS
    for sensor_def in RUNTIME_SENSORS:
        if sensor_def.get("type", "") == "sensor":
            entities.append(
                EG4InverterSensor(coordinator, entry, sensor_def, parent_key="runtime")
            )

    # 4.3) SETTINGS SENSORS
    for sensor_def in SETTING_SENSORS:
        if sensor_def.get("type", "") == "sensor":
            entities.append(
                EG4InverterSensor(coordinator, entry, sensor_def, parent_key="settings")
            )

    # 4.4) BATTERY SUMMARY SENSORS
    for sensor_def in BATTERY_SUMMARY_SENSORS:
        if sensor_def.get("type", "") == "sensor":
            entities.append(
                EG4InverterSensor(coordinator, entry, sensor_def, parent_key="battery")
            )

    # 4.5) PER-BATTERY UNITS
    #     If you want a sensor for each battery in battery_units, create them here:
    battery_data = coordinator.data.get("battery", {})
    battery_units = battery_data.battery_units or []
    for binfo in battery_units:
        for subdef in PER_BATTERY_DEFS:
            subdef = subdef.copy()
            if subdef["type"] != "sensor":
                continue
            name_template = subdef.get("name", "")
            dynamic_name = name_template.format(binfo=binfo)
            if name_template != dynamic_name:
                subdef["name"] = dynamic_name
            entities.append(EG4PerBatterySensor(coordinator, entry, binfo, subdef))

    async_add_entities(entities)


# -------------------------------------------------------------------------
# 5) BASE SENSOR CLASSES
# -------------------------------------------------------------------------
class EG4BaseSensor(SensorEntity):
    """Common base for EG4 sensors that integrates with the coordinator."""

    def __init__(self, coordinator, entry):
        """Initialize the base sensor."""
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


class EG4InverterSensor(EG4BaseSensor):
    """A sensor for a single data point in either energy, runtime, or battery summary."""

    def __init__(self, coordinator, entry, sensor_def: Dict[str, Any], parent_key: str):
        super().__init__(coordinator, entry)
        self._sensor_def = sensor_def
        self._parent_key = parent_key

        # Build a unique_id from the config entry + sensor key
        self._attr_unique_id = f"{entry.entry_id}_{parent_key}_{sensor_def['key']}"
        self._attr_name = sensor_def.get("name", sensor_def["key"])

        # Optional icon or device_class
        icon = sensor_def.get("icon")
        if icon:
            self._attr_icon = icon

        self._attr_device_class = sensor_def.get("device_class")
        self._attr_state_class = sensor_def.get("state_class")

        # Unit of measurement
        self._unit = sensor_def.get("unit")
        self._scale = sensor_def.get("scale", 1.0)
        calc = sensor_def.get("calc")
        if calc:
            self._calc = calc

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        data = self._coordinator.data.get(self._parent_key, {})
        try:
            raw_value = getattr(data, self._sensor_def["key"])
        except Exception as e:
            try:
                raw_value = data.get(self._sensor_def["key"])
            except Exception as e2:
                _LOGGER.error(f"{self._sensor_def} with error {e2}")
                _LOGGER.error(f"Data {vars(data)}")
                return None

        # Special case: parse CO2/Coal text like "367.69 kG"
        if self._sensor_def.get("co2_parse"):
            # Extract float portion
            return parse_float(str(raw_value).split(" ")[0], 1.0)

        # Otherwise, try to parse as float if the sensor is numeric
        if self._unit or self._scale != 1.0:
            return parse_float(raw_value, self._scale)

        # If it's truly a string (like "statusText"), just return it
        return raw_value


class EG4PerBatterySensor(EG4BaseSensor):
    """A sensor for each battery in battery_units."""

    def __init__(
        self,
        coordinator,
        entry,
        battery_info: Dict[str, Any],
        sensor_def: Dict[str, Any],
    ):
        super().__init__(coordinator, entry)
        self._sensor_def = sensor_def.copy()
        self._bat_index = battery_info.batIndex

        key = sensor_def["key"]
        self._attr_unique_id = f"{entry.entry_id}_battery_{self._bat_index}_{key}"
        self._attr_name = sensor_def.get("name", f"{self._bat_index} {key}")
        self._unit = sensor_def.get("unit")
        self._scale = sensor_def.get("scale", 1.0)
        self._attr_device_class = sensor_def.get("device_class")
        self._attr_state_class = sensor_def.get("state_class")
        icon = sensor_def.get("icon")
        if icon:
            self._attr_icon = icon
        calc = sensor_def.get("calc")
        if calc:
            self._calc = calc

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        battery_data = self._coordinator.data.get("battery", {})
        battery_units = getattr(battery_data, "battery_units", [])

        # Lookup battery by index
        target = next((b for b in battery_units if getattr(b, "batIndex", None) == self._bat_index), None)
        if target is None:
            return None

        try:
            raw_value = getattr(target, self._sensor_def["key"])
        except Exception:
            raw_value = target.get(self._sensor_def["key"])

        if self._unit or self._scale != 1.0:
            return parse_float(raw_value, self._scale)
        return raw_value
