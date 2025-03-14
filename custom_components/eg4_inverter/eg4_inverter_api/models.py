class Inverter:
    """Represents an EG4 Inverter."""

    def __init__(self, plantId, plantName, captureExtra=True, **kwargs) -> None:
        self.plantId = plantId
        self.plantName = plantName
        self.serialNum = None
        self._main_args = [
            "serialNum",
            "phase",
            "dtc",
            "deviceType",
            "subDeviceType",
            "allowExport2Grid",
            "batteryType",
            "standard",
            "slaveVersion",
            "fwVersion",
            "allowGenExercise",
            "withbatteryData",
            "hardwareVersion",
            "voltClass",
            "machineType",
            "protocolVersion",
        ]
        for key in self._main_args:
            setattr(self, key, kwargs.get(key))

        if captureExtra:
            self.from_dict(
                {x: y for x, y in kwargs.items() if x not in self._main_args}
            )

    def from_dict(self, d):
        """Set values based on dictionary."""
        for key, value in d.items():
            setattr(self, key, value)

    def __repr__(self):
        return (
            "Inverter("
            f"serialNum={self.serialNum}, plantName={self.plantName} "
            f"plantName={self.plantId}, batteryType={self.batteryType}, "
            f"fwVersion={self.fwVersion}, phase={self.phase}"
            ")"
        )


class BatteryUnit:
    """Represents an individual battery unit."""

    def __init__(self, captureExtra=True, **kwargs):
        """Initialize BatteryUnit."""
        self._main_args = [
            "batteryKey",
            "batIndex",
            "batterySn",
            "totalVoltage",
            "current",
            "soc",
            "soh",
            "cycleCnt",
        ]
        for key in self._main_args:
            setattr(self, key, kwargs.get(key))

        # Capture any unknown or new API fields dynamically
        if captureExtra:
            self.from_dict(
                {x: y for x, y in kwargs.items() if x not in self._main_args}
            )

    def from_dict(self, d) -> None:
        """Set values based on dictionary."""
        for key, value in d.items():
            setattr(self, key, value)

    def to_dict(self):
        """Return the battery unit as a dictionary."""
        return self.__dict__

    def __repr__(self):
        return f"BatteryUnit({self.batIndex}: sn {self.batterySn}, soc% {self.soc}, soh% {self.soh}, cycles {self.cycleCnt}, v {self.totalVoltage / 100}, )"


class BatteryData:
    """Represents overall battery data including individual battery units."""

    def __init__(
        self,
        remainCapacity,
        fullCapacity,
        totalNumber,
        totalVoltageText,
        currentText,
        battery_units=[],
    ):
        self.remainCapacity = remainCapacity
        self.fullCapacity = fullCapacity
        self.totalNumber = totalNumber
        self.totalVoltageText = totalVoltageText
        self.currentText = currentText

        # Battery units as a list
        self.battery_units = battery_units if battery_units else []

    def to_dict(self):
        """Return the battery data including individual units as a dictionary."""
        data = self.__dict__.copy()
        data["battery_units"] = [unit.to_dict() for unit in self.battery_units]
        return data

    def __repr__(self):
        d = self.to_dict()
        data = {x: y for x, y in d.items() if x != "battery_units"}
        return f"BatteryData({data.items()} )"


class EnergyData:
    """Represents inverter energy data from the API."""

    def __init__(self, captureExtra=True, **kwargs):
        self._main_args = [
            "todayYielding",
            "totalYielding",
            "todayDischarging",
            "totalDischarging",
            "todayCharging",
            "totalCharging",
            "todayImport",
            "totalImport",
            "todayExport",
            "totalExport",
            "todayUsage",
            "totalUsage",
        ]
        for key in self._main_args:
            setattr(self, key, kwargs.get(key))

        # Capture any unknown or new API fields dynamically
        if captureExtra:
            self.from_dict(
                {x: y for x, y in kwargs.items() if x not in self._main_args}
            )

    def from_dict(self, d) -> None:
        """Set values based on dictionary."""
        for key, value in d.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"EnergyData({self.to_dict()})"

    def to_dict(self):
        return self.__dict__


class RuntimeData:
    """Represents inverter runtime data from the API."""

    def __init__(
        self,
        captureExtra=True,
        **kwargs,
    ):
        self._main_args = [
            "statusText",
            "batteryType",
            "batParallelNum",
            "batCapacity",
            "consumptionPower",
            "vpv1",
            "vpv2",
            "vpv3",
            "vpv4",
            "ppvpCharge",
            "pDisCharge",
            "peps",
            "pToGrid",
            "pToUser",
        ]
        for key in self._main_args:
            setattr(self, key, kwargs.get(key))

        # Capture any unknown or new API fields dynamically
        if captureExtra:
            d = {x: y for x, y in kwargs.items() if x not in self._main_args}
            self.from_dict(d)

    def from_dict(self, d) -> None:
        """Set values based on dictionary."""
        for key, value in d.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"RuntimeData({self.to_dict()})"

    def to_dict(self):
        return self.__dict__

class InverterParameters:
    """Represents inverter parameters."""

    def __init__(
        self
    ):
        self._skip_args = ["valueFrame","inverterSn","startRegister","pointNumber"]
        self._main_args = ["success"]
        self.success=True

    def from_dict(self, d) -> None:
        """Set values based on dictionary."""
        for key, value in d.items():
            if key not in self._main_args and key not in self._skip_args:
                setattr(self, key, value)

    def __repr__(self):
        return f"RuntimeData({self.to_dict()})"

    def to_dict(self):
        return self.__dict__


class APIResponse:
    """A general-purpose response model for handling success/failure states."""

    def __init__(self, success, data=None, error_message=None):
        self.success = success
        self.data = data
        self.error_message = error_message

    def __repr__(self):
        return f"APIResponse(success={self.success}, data={self.data}, error={self.error_message})"
