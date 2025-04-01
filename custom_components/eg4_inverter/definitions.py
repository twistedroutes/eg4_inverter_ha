# definitions.py

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

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

# -------------------------------------------------------------------------
# 1) ENERGY SENSORS
#    Data from coordinator.data["energy"]
#    Original fields in get_inverter_energy_async() sample
# -------------------------------------------------------------------------
ENERGY_SENSORS = [
    {
        "type": "sensor",
        "key": "soc",
        "name": "Battery State of Charge",
        "unit": PERCENTAGE,
        "device_class": "battery",  # or SensorDeviceClass.BATTERY if you import it
        "entity_category": None,
        "description": "Battery SoC from energy data",
    },
    {
        "type": "sensor",
        "key": "todayYieldingText",  # "9.2" => interpret as 9.2 kWh
        "name": "Solar Generation Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:solar-power",
        "description": "Energy generated today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalYieldingText",  # e.g. "368.8" => interpret as 368.8 kWh
        "name": "Solar Generation Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:solar-power",
        "description": "Lifetime energy generated (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "todayDischargingText",
        "name": "Battery Discharging Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-heart",
        "description": "Energy discharged from battery today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalDischargingText",
        "name": "Battery Discharging Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-heart",
        "description": "Lifetime battery discharge (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "todayChargingText",
        "name": "Battery Charging Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-charging",
        "description": "Energy charged into battery today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalChargingText",
        "name": "Battery Discharging Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:battery-charging",
        "description": "Lifetime battery charge (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "todayUsageText",
        "name": "Energy Consumption Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:home-import-outline",
        "description": "Energy consumed by the home today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalUsageText",
        "name": "Energy Consumption Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:home-import-outline",
        "description": "Lifetime energy consumed by the home (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "todayImportText",
        "name": "Imported from Grid Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-import",
        "description": "Energy imported from grid today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalImportText",
        "name": "Imported from Grid Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-import",
        "description": "Lifetime energy imported from the grid (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "todayExportText",
        "name": "Exported to Grid Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-export",
        "description": "Energy exported to grid today (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "type": "sensor",
        "key": "totalExportText",
        "name": "Exported to Grid Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "icon": "mdi:transmission-tower-export",
        "description": "Lifetime energy exported to the grid (kWh)",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "type": "sensor",
        "key": "totalCo2ReductionText",  # e.g. "367.69 kG"
        "name": "CO2 Reduction",
        "unit": UnitOfMass.KILOGRAMS,
        "icon": "mdi:molecule-co2",
        "description": "Total CO2 reduction in kg",
        "co2_parse": True,  # We'll parse the numeric portion
    },
    {
        "type": "sensor",
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
        "type": "sensor",
        "key": "lost",
        "name": "Inverter Lost State (Raw)",
        "unit": None,
        "icon": "mdi:alert",
        "description": "Indicates if inverter is lost/offline (True/False)",
    },
    {
        "type": "sensor",
        "key": "statusText",
        "name": "Inverter Status Text",
        "unit": None,
        "icon": "mdi:information-outline",
    },
    {
        "type": "sensor",
        "key": "batteryType",
        "name": "Battery Type",
        "unit": None,
    },
    {
        "type": "sensor",
        "key": "batCapacity",  # Raw Amp-hours from the device
        "name": "Battery Capacity",
        "unit": "kWh",
        "icon": "mdi:battery",  # or an appropriate icon
        "scale": 0.0512,  # 51.2 / 1000
        "description": "Battery capacity in kWh (converted from Ah at 51.2V nominal)",
    },
    {
        "type": "sensor",
        "key": "vpv1",
        "name": "PV1 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,  # if 2098 => 20.98, adjust if needed
        "icon": "mdi:solar-panel",
    },
    {
        "type": "sensor",
        "key": "vpv2",
        "name": "PV2 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,
        "icon": "mdi:solar-panel",
    },
    {
        "type": "sensor",
        "key": "vpv3",
        "name": "PV3 Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,
        "icon": "mdi:solar-panel",
    },
    {
        "type": "sensor",
        "key": "ppv1",
        "name": "PV1 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "type": "sensor",
        "key": "ppv2",
        "name": "PV2 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "type": "sensor",
        "key": "ppv3",
        "name": "PV3 Power",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:flash",
    },
    {
        "type": "sensor",
        "key": "vacr",  # e.g. 6145 => 61.45 V? Or is it AC voltage in 0.1?
        "name": "AC Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.1,
    },
    {
        "type": "sensor",
        "key": "vepsr",  # e.g. 6145 => 61.45 V? Or is it AC voltage in 0.1?
        "name": "EPS Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.1,
    },
    {
        "type": "sensor",
        "key": "fac",
        "name": "AC Frequency",
        "unit": UnitOfFrequency.HERTZ,
        "scale": 0.01,
    },
    {
        "type": "sensor",
        "key": "feps",
        "name": "EPS Frequency",
        "unit": UnitOfFrequency.HERTZ,
        "scale": 0.01,
    },
    {
        "type": "sensor",
        "key": "pToGrid",
        "name": "Power to Grid",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:transmission-tower-export",
    },
    {
        "type": "sensor",
        "key": "pToUser",
        "name": "Power to User Load",
        "unit": UnitOfPower.WATT,
        "icon": "mdi:home-import-outline",
    },
    {
        "type": "sensor",
        "key": "tradiator1",
        "name": "Radiator Temp 1",
        "unit": UnitOfTemperature.CELSIUS,
    },
    {
        "type": "sensor",
        "key": "tradiator2",
        "name": "Radiator Temp 2",
        "unit": UnitOfTemperature.CELSIUS,
    },
    {
        "type": "sensor",
        "key": "soc",
        "name": "Runtime SoC",
        "unit": PERCENTAGE,
        "description": "Battery SoC from runtime data",
    },
    {
        "type": "sensor",
        "key": "vBat",
        "name": "Battery Voltage (Raw)",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.1,  # 530 => 53.0
    },
    {
        "type": "sensor",
        "key": "pCharge",
        "name": "Battery Charging Power",
        "unit": UnitOfPower.WATT,
    },
    {
        "type": "sensor",
        "key": "pDisCharge",
        "name": "Battery Discharging Power",
        "unit": UnitOfPower.WATT,
    },
    {
        "type": "sensor",
        "key": "batPower",
        "name": "Battery Power (Net)",
        "unit": UnitOfPower.WATT,
        "description": "Negative => Discharging, Positive => Charging",
    },
    {
        "type": "sensor",
        "key": "maxChgCurrValue",
        "name": "Max Charge Current",
        "unit": "A",  # or UnitOfElectricCurrent.AMPERE
    },
    {
        "type": "sensor",
        "key": "maxDischgCurrValue",
        "name": "Max Discharge Current",
        "unit": "A",
    },
    {
        "type": "sensor",
        "key": "genVolt",
        "name": "Generator Voltage",
        "unit": UnitOfElectricPotential.VOLT,
    },
    {
        "type": "sensor",
        "key": "genFreq",
        "name": "Generator Frequency",
        "unit": UnitOfFrequency.HERTZ,
    },
    {
        "type": "sensor",
        "key": "consumptionPower",
        "name": "Consumption Power",
        "unit": UnitOfPower.WATT,
        "description": "Load consumption power if provided",
    },
    {
        "type": "sensor",
        "key": "fwCode",
        "name": "Firmware Code",
        "unit": None,
        "description": "Load consumption power if provided",
    },
    {
        "type": "binary_sensor",
        "key": "genDryContact",
        "name": "Generator Dry Contact",
        "calc": lambda runtime: bool(runtime.genDryContact == "ON"),
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
    },
    {
        "type": "binary_sensor",
        "key": "_12KUsingGenerator",
        "name": "12K Generator State",
        "device_class": BinarySensorDeviceClass.CONNECTIVITY,
    },
    {
        "type": "binary_sensor",
        "key": "bmsCharge",
        "name": "BMS Allow Charging",
        "device_class": BinarySensorDeviceClass.BATTERY_CHARGING,
    },
    {
        "type": "binary_sensor",
        "key": "bmsDischarge",
        "name": "BMS Allow Discharging",
        "device_class": BinarySensorDeviceClass.BATTERY_CHARGING,
    },
]


# -------------------------------------------------------------------------
# 3) BATTERY SUMMARY SENSORS
#    Data from coordinator.data["battery"] (the high-level summary),
#    not the per-battery details in battery["battery_units"].
# -------------------------------------------------------------------------
BATTERY_SUMMARY_SENSORS = [
    {
        "type": "sensor",
        "key": "remainCapacity",
        "name": "Battery Remain Capacity",
        "unit": "kWh",
        "scale": 0.0512,
    },
    {
        "type": "sensor",
        "key": "fullCapacity",
        "name": "Battery Full Capacity",
        "unit": "kWh",
        "icon": "mdi:battery",  # or an appropriate icon
        "scale": 0.0512,
    },
    {
        "type": "sensor",
        "key": "currentText",
        "name": "Battery Current Text",
        "unit": "A",
        "description": "String representation of current, e.g. '-5.1'",
    },
    {
        "type": "sensor",
        "key": "totalNumber",
        "name": "Number of Batteries",
        "unit": None,
        "description": "Count of the number of batteries identified by the inverter",
    },
    {
        "type": "sensor",
        "key": "totalVoltageText",
        "name": "Battery Voltage (Text)",
        "unit": UnitOfElectricPotential.VOLT,
    },
]


# "per-battery" definitions that apply to multiple platforms
PER_BATTERY_DEFS = [
    {
        "type": "sensor",
        "key": "batterySn",
        "name": "Battery {binfo.batIndex} SN",
        "unit": PERCENTAGE,
    },
    {
        "type": "sensor",
        "key": "soc",
        "name": "Battery {binfo.batIndex} SoC",
        "unit": PERCENTAGE,
    },
    {
        "type": "sensor",
        "key": "totalVoltage",
        "name": "Battery {binfo.batIndex} Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.01,  # 5333 => 53.33 if needed
    },
    {
        "type": "sensor",
        "key": "current",
        "name": "Battery {binfo.batIndex} Current",
        "unit": "A",  # negative => discharge
    },
    {
        "type": "sensor",
        "key": "soh",
        "name": "Battery {binfo.batIndex} SoH",
        "unit": PERCENTAGE,
    },
    {
        "type": "sensor",
        "key": "cycleCnt",
        "name": "Battery {binfo.batIndex} Cycles",
        "unit": None,
    },
    {
        "type": "sensor",
        "key": "batMaxCellTemp",
        "name": "Battery {binfo.batIndex} Max Cell Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "scale": 0.1,
    },
    {
        "type": "sensor",
        "key": "batMinCellTemp",
        "name": "Battery {binfo.batIndex} Min Cell Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "scale": 0.1,
    },
    {
        "type": "sensor",
        "key": "batMaxCellVoltage",
        "name": "Battery {binfo.batIndex} Max Cell Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.001,
    },
    {
        "type": "sensor",
        "key": "batMinCellVoltage",
        "name": "Battery {binfo.batIndex} Min Cell Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 0.001,
    },
    {
        "type": "sensor",
        "key": "fwVersionText",
        "name": "Battery {binfo.batIndex} Firmware Version",
        "unit": None,
    },
    {
        "type": "sensor",
        "key": "noticeInfo",
        "name": "Battery {binfo.batIndex} Notice Text",
        "unit": None,
    },
    {
        "type": "binary_sensor",
        "key": "notice",
        "name": "Battery {binfo.batIndex} Notice Active",
        "calc": lambda binfo: bool(binfo.noticeInfo),
        "device_class": BinarySensorDeviceClass.TAMPER,
    },
]

SETTING_SENSORS = [
    {
        "type": "sensor",
        "key": "HOLD_EPS_FREQ_SET",
        "name": "EG4 EPS Frequency Setting",
        "unit": None,
        "unit": UnitOfFrequency.HERTZ,
        "scale": 1,
    },
    {
        "type": "sensor",
        "key": "HOLD_EPS_VOLT_SET",
        "name": "EG4 EPS Voltage Setting",
        "unit": None,
        "unit": UnitOfElectricPotential.VOLT,
        "scale": 1,
    }
]
