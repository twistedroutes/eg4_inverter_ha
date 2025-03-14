import logging
from typing import Any, Dict
from homeassistant.components.sensor import SensorEntity
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
# 1) ENERGY SENSORS
#    Data from coordinator.data["energy"]
#    Original fields in get_inverter_energy_async() sample
# -------------------------------------------------------------------------
ENERGY_SENSORS = [
    {
        "key": "soc",
        "name": "Battery State of Charge",
        "unit": PERCENTAGE,
        "device_class": "battery",  # or SensorDeviceClass.BATTERY if you import it
        "entity_category": None,
        "description": "Battery SoC from energy data",
    },
    {
        "key": "todayYieldingText",  # "9.2" => interpret as 9.2 kWh
        "name": "Today Yielding",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:solar-power",
        "description": "Energy generated today (kWh)",
    },
    {
        "key": "totalYieldingText",  # e.g. "368.8" => interpret as 368.8 kWh
        "name": "Total Yielding",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:solar-power",
        "description": "Lifetime energy generated (kWh)",
    },
    {
        "key": "todayDischargingText",
        "name": "Today Discharging",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-heart",
        "description": "Energy discharged from battery today (kWh)",
    },
    {
        "key": "totalDischargingText",
        "name": "Total Discharging",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-heart",
        "description": "Lifetime battery discharge (kWh)",
    },
    {
        "key": "todayChargingText",
        "name": "Today Charging",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-charging",
        "description": "Energy charged into battery today (kWh)",
    },
    {
        "key": "totalChargingText",
        "name": "Total Charging",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-charging",
        "description": "Lifetime battery charge (kWh)",
    },
    {
        "key": "todayUsageText",
        "name": "Today Usage",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:home-import-outline",
        "description": "Energy consumed by the home today (kWh)",
    },
    {
        "key": "totalUsageText",
        "name": "Total Usage",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:home-import-outline",
        "description": "Lifetime energy consumed by the home (kWh)",
    },
    {
        "key": "todayImportText",
        "name": "Today Imported from Grid",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-import",
        "description": "Energy imported from grid today (kWh)",
    },
    {
        "key": "totalImportText",
        "name": "Total Imported from Grid",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-import",
        "description": "Lifetime energy imported from the grid (kWh)",
    },
    {
        "key": "todayExportText",
        "name": "Today Exported to Grid",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-export",
        "description": "Energy exported to grid today (kWh)",
    },
    {
        "key": "totalExportText",
        "name": "Total Exported to Grid",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-export",
        "description": "Lifetime energy exported to the grid (kWh)",
    },
    {
        "key": "totalCo2ReductionText",  # e.g. "367.69 kG"
        "name": "CO2 Reduction",
        "unit": UnitOfMass.KILOGRAMS,
        "icon": "mdi:molecule-co2",
        "description": "Total CO2 reduction in kg",
        "co2_parse": True,  # We'll parse the numeric portion
    },
    {
        "key": "totalCoalReductionText",  # e.g. "147.52 kG"
        "name": "Coal Reduction",
        "unit": UnitOfMass.KILOGRAMS,
        "icon": "mdi:factory",
        "description": "Total coal reduction in kg",
        "co2_parse": True,
    },
]

# -------------------------------------------------------------------------
# 2) RUNTIME SENSORS
#    Data from coordinator.data["runtime"]
#    Original fields in get_inverter_runtime_async() sample
# -------------------------------------------------------------------------
RUNTIME_SENSORS = [
    {
        "key": "lost",
        "name": "Inverter Lost State (Raw)",
        "unit": None,
        "icon": "mdi:alert",
        "description": "Indicates if inverter is lost/offline (True/False)",
    },
    {
        "key": "statusText",
        "name": "Inverter Status Text",
        "unit": None,
        "icon": "mdi:information-outline",
    },
    {
        "key": "batteryType",
        "name": "Battery Type",
        "unit": None,
    },
    {
        "key": "batCapacity",  # Raw Amp-hours from the device
        "name": "Battery Capacity",
        "unit": "kWh",
        "icon": "mdi:battery",  # or an appropriate icon
        "scale": 0.0512,  # 51.2 / 1000
        "description": "Battery capacity in kWh (converted from Ah at 51.2V nominal)",
    },
    {
        "key": "vpv1",
        "name": "PV1 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,  # if 2098 => 20.98, adjust if needed
        "icon": "mdi:solar-panel",
    },
    {
        "key": "vpv2",
        "name": "PV2 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,
        "icon": "mdi:solar-panel",
    },
    {
        "key": "vpv3",
        "name": "PV3 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,
        "icon": "mdi:solar-panel",
    },
    {
        "key": "ppv1",
        "name": "PV1 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "key": "ppv2",
        "name": "PV2 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "key": "ppv3",
        "name": "PV3 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "key": "vact",  # e.g. 6145 => 61.45 V? Or is it AC voltage in 0.1?
        "name": "AC Total Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,
    },
    {
        "key": "fac",
        "name": "AC Frequency",
        "unit": UnitOfFrequency.HERTZ,
        "scale": 0.01,
    },
    {
        "key": "pToGrid",
        "name": "Power to Grid",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:transmission-tower-export",
    },
    {
        "key": "pToUser",
        "name": "Power to User Load",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:home-import-outline",
    },
    {
        "key": "tradiator1",
        "name": "Radiator Temp 1",
        "unit": UnitOfTemperature.CELSIUS,
    },
    {
        "key": "tradiator2",
        "name": "Radiator Temp 2",
        "unit": UnitOfTemperature.CELSIUS,
    },
    {
        "key": "soc",
        "name": "Runtime SoC",
        "unit": PERCENTAGE,
        "description": "Battery SoC from runtime data",
    },
    {
        "key": "vBat",
        "name": "Battery Voltage (Raw)",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.1,  # 530 => 53.0
    },
    {
        "key": "pCharge",
        "name": "Battery Charging Power",
        "unit": UnitOfPower.WATT,
    },
    {
        "key": "pDisCharge",
        "name": "Battery Discharging Power",
        "unit": UnitOfPower.WATT,
    },
    {
        "key": "batPower",
        "name": "Battery Power (Net)",
        "unit": UnitOfPower.WATT,
        "description": "Negative => Discharging, Positive => Charging",
    },
    {
        "key": "maxChgCurrValue",
        "name": "Max Charge Current",
        "unit": "A",  # or UnitOfElectricCurrent.AMPERE
    },
    {
        "key": "maxDischgCurrValue",
        "name": "Max Discharge Current",
        "unit": "A",
    },
    {
        "key": "genVolt",
        "name": "Generator Voltage",
        "unit": UnitOfElectricPotential.VOLT,
    },
    {
        "key": "genFreq",
        "name": "Generator Frequency",
        "unit": UnitOfFrequency.HERTZ,
    },
    {
        "key": "consumptionPower",
        "name": "Consumption Power",
        "unit": UnitOfPower.WATT,
        "description": "Load consumption power if provided",
    },
]

# -------------------------------------------------------------------------
# 3) BATTERY SUMMARY SENSORS
#    Data from coordinator.data["battery"] (the high-level summary),
#    not the per-battery details in battery["battery_units"].
# -------------------------------------------------------------------------
BATTERY_SUMMARY_SENSORS = [
    {
        "key": "remainCapacity",
        "name": "Battery Remain Capacity",
        "unit": "kWh",
        "scale": 0.0512,
    },
    {
        "key": "fullCapacity",
        "name": "Battery Full Capacity",
        "unit": "kWh",
        "icon": "mdi:battery",  # or an appropriate icon
        "scale": 0.0512,
    },
    {
        "key": "currentText",
        "name": "Battery Current Text",
        "unit": "A",
        "description": "String representation of current, e.g. '-5.1'",
    },
    {
        "key": "totalVoltageText",
        "name": "Battery Voltage (Text)",
        "unit": UnitOfElectricPotential.VOLT,
    },
]


# -------------------------------------------------------------------------
# 4) SETUP: CREATE ENTITIES FROM DEFINITIONS
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
        entities.append(
            EG4InverterSensor(coordinator, entry, sensor_def, parent_key="energy")
        )

    # 4.2) RUNTIME SENSORS
    for sensor_def in RUNTIME_SENSORS:
        entities.append(
            EG4InverterSensor(coordinator, entry, sensor_def, parent_key="runtime")
        )

    # 4.3) BATTERY SUMMARY SENSORS
    for sensor_def in BATTERY_SUMMARY_SENSORS:
        entities.append(
            EG4InverterSensor(coordinator, entry, sensor_def, parent_key="battery")
        )

    # 4.4) PER-BATTERY UNITS
    #     If you want a sensor for each battery in battery_units, create them here:
    battery_data = coordinator.data.get("battery", {})
    battery_units = battery_data.battery_units or []
    for binfo in battery_units:
        # We'll create a handful of sensors for each physical battery
        # You can expand this list as needed
        per_battery_defs = [
            {
                "key": "soc",
                "name": f"Battery {binfo.batterySn} SoC",
                "unit": PERCENTAGE,
            },
            {
                "key": "totalVoltage",
                "name": f"Battery {binfo.batterySn} Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "scale": 0.01,  # 5333 => 53.33 if needed
            },
            {
                "key": "current",
                "name": f"Battery {binfo.batterySn} Current",
                "unit": "A",  # negative => discharge
            },
            {
                "key": "soh",
                "name": f"Battery {binfo.batterySn} SoH",
                "unit": PERCENTAGE,
            },
            {
                "key": "cycleCnt",
                "name": f"Battery {binfo.batterySn} Cycles",
                "unit": None,
            },
            {
                "key": "batMaxCellTemp",
                "name": f"Battery {binfo.batterySn} Max Cell Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "scale": 0.1,
            },
            {
                "key": "batMinCellTemp",
                "name": f"Battery {binfo.batterySn} Min Cell Temperature",
                "unit": UnitOfTemperature.CELSIUS,
                "scale": 0.1,
            },
            {
                "key": "batMaxCellVoltage",
                "name": f"Battery {binfo.batterySn} Max Cell Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "scale": 0.001,
            },
            {
                "key": "batMinCellVoltage",
                "name": f"Battery {binfo.batterySn} Min Cell Voltage",
                "unit": UnitOfElectricPotential.VOLT,
                "scale": 0.001,
            },
            {
                "key": "fwVersionText",
                "name": f"Battery {binfo.batterySn} Firmware Version",
                "unit": None,
            },
        ]
        for subdef in per_battery_defs:
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

        device_class = sensor_def.get("device_class")
        if device_class:
            self._attr_device_class = device_class

        # Unit of measurement
        self._unit = sensor_def.get("unit")
        self._scale = sensor_def.get("scale", 1.0)

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        data = self._coordinator.data.get(self._parent_key, {})
        try:
            raw_value = getattr(data, self._sensor_def["key"])
        except Exception as e:
            raw_value = data.get(self._sensor_def["key"])

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
        self._battery_info = battery_info
        self._sensor_def = sensor_def

        battery_sn = battery_info.batterySn or "Unknown"
        key = sensor_def["key"]
        self._attr_unique_id = f"{entry.entry_id}_battery_{battery_sn}_{key}"
        self._attr_name = sensor_def.get("name", f"{battery_sn} {key}")
        self._unit = sensor_def.get("unit")
        self._scale = sensor_def.get("scale", 1.0)

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        try:
            raw_value = getattr(self._battery_info, self._sensor_def["key"])
        except Exception as e:
            raw_value = self._battery_info.get(self._sensor_def["key"])

        # Attempt float parse if there's a unit or scale
        if self._unit or self._scale != 1.0:
            return parse_float(raw_value, self._scale)

        return raw_value
