from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence, List, Tuple

from typing_extensions import Self
from viam.components.movement_sensor import MovementSensor, GeoPoint, Vector3, Orientation
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Geometry
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

import obd

def quantity_to_array(quantity):
    """
    Convert a pint.Quantity to an array of length 2 where index 0 is the scalar
    and index 1 is the unit as a string.

    Parameters:
    quantity (pint.Quantity): The quantity to convert.

    Returns:
    list: A list where index 0 is the scalar value and index 1 is the unit.
    """
    return [quantity.magnitude, str(quantity.units)]

obd_commands = {
    "STATUS": obd.commands.STATUS,
    "FUEL_STATUS": obd.commands.FUEL_STATUS,
    "ENGINE_LOAD": obd.commands.ENGINE_LOAD,
    "COOLANT_TEMP": obd.commands.COOLANT_TEMP,
    "SPEED": obd.commands.SPEED,
    "PIDS_A": obd.commands.PIDS_A,
    "FREEZE_DTC": obd.commands.FREEZE_DTC,
    "SHORT_FUEL_TRIM_1": obd.commands.SHORT_FUEL_TRIM_1,
    "LONG_FUEL_TRIM_1": obd.commands.LONG_FUEL_TRIM_1,
    "SHORT_FUEL_TRIM_2": obd.commands.SHORT_FUEL_TRIM_2,
    "LONG_FUEL_TRIM_2": obd.commands.LONG_FUEL_TRIM_2,
    "FUEL_PRESSURE": obd.commands.FUEL_PRESSURE,
    "INTAKE_PRESSURE": obd.commands.INTAKE_PRESSURE,
    "RPM": obd.commands.RPM,
    "TIMING_ADVANCE": obd.commands.TIMING_ADVANCE,
    "INTAKE_TEMP": obd.commands.INTAKE_TEMP,
    "MAF": obd.commands.MAF,
    "THROTTLE_POS": obd.commands.THROTTLE_POS,
    "AIR_STATUS": obd.commands.AIR_STATUS,
    "O2_SENSORS": obd.commands.O2_SENSORS,
    "O2_B1S1": obd.commands.O2_B1S1,
    "O2_B1S2": obd.commands.O2_B1S2,
    "O2_B1S3": obd.commands.O2_B1S3,
    "O2_B1S4": obd.commands.O2_B1S4,
    "O2_B2S1": obd.commands.O2_B2S1,
    "O2_B2S2": obd.commands.O2_B2S2,
    "O2_B2S3": obd.commands.O2_B2S3,
    "O2_B2S4": obd.commands.O2_B2S4,
    "OBD_COMPLIANCE": obd.commands.OBD_COMPLIANCE,
    "O2_SENSORS_ALT": obd.commands.O2_SENSORS_ALT,
    "AUX_INPUT_STATUS": obd.commands.AUX_INPUT_STATUS,
    "RUN_TIME": obd.commands.RUN_TIME,
    "PIDS_B": obd.commands.PIDS_B,
    "DISTANCE_W_MIL": obd.commands.DISTANCE_W_MIL,
    "FUEL_RAIL_PRESSURE_VAC": obd.commands.FUEL_RAIL_PRESSURE_VAC,
    "FUEL_RAIL_PRESSURE_DIRECT": obd.commands.FUEL_RAIL_PRESSURE_DIRECT,
    "O2_S1_WR_VOLTAGE": obd.commands.O2_S1_WR_VOLTAGE,
    "O2_S2_WR_VOLTAGE": obd.commands.O2_S2_WR_VOLTAGE,
    "O2_S3_WR_VOLTAGE": obd.commands.O2_S3_WR_VOLTAGE,
    "O2_S4_WR_VOLTAGE": obd.commands.O2_S4_WR_VOLTAGE,
    "O2_S5_WR_VOLTAGE": obd.commands.O2_S5_WR_VOLTAGE,
    "O2_S6_WR_VOLTAGE": obd.commands.O2_S6_WR_VOLTAGE,
    "O2_S7_WR_VOLTAGE": obd.commands.O2_S7_WR_VOLTAGE,
    "O2_S8_WR_VOLTAGE": obd.commands.O2_S8_WR_VOLTAGE,
    "COMMANDED_EGR": obd.commands.COMMANDED_EGR,
    "EGR_ERROR": obd.commands.EGR_ERROR,
    "EVAPORATIVE_PURGE": obd.commands.EVAPORATIVE_PURGE,
    "FUEL_LEVEL": obd.commands.FUEL_LEVEL,
    "WARMUPS_SINCE_DTC_CLEAR": obd.commands.WARMUPS_SINCE_DTC_CLEAR,
    "DISTANCE_SINCE_DTC_CLEAR": obd.commands.DISTANCE_SINCE_DTC_CLEAR,
    "EVAP_VAPOR_PRESSURE": obd.commands.EVAP_VAPOR_PRESSURE,
    "BAROMETRIC_PRESSURE": obd.commands.BAROMETRIC_PRESSURE,
    "O2_S1_WR_CURRENT": obd.commands.O2_S1_WR_CURRENT,
    "O2_S2_WR_CURRENT": obd.commands.O2_S2_WR_CURRENT,
    "O2_S3_WR_CURRENT": obd.commands.O2_S3_WR_CURRENT,
    "O2_S4_WR_CURRENT": obd.commands.O2_S4_WR_CURRENT,
    "O2_S5_WR_CURRENT": obd.commands.O2_S5_WR_CURRENT,
    "O2_S6_WR_CURRENT": obd.commands.O2_S6_WR_CURRENT,
    "O2_S7_WR_CURRENT": obd.commands.O2_S7_WR_CURRENT,
    "O2_S8_WR_CURRENT": obd.commands.O2_S8_WR_CURRENT,
    "CATALYST_TEMP_B1S1": obd.commands.CATALYST_TEMP_B1S1,
    "CATALYST_TEMP_B2S1": obd.commands.CATALYST_TEMP_B2S1,
    "CATALYST_TEMP_B1S2": obd.commands.CATALYST_TEMP_B1S2,
    "CATALYST_TEMP_B2S2": obd.commands.CATALYST_TEMP_B2S2,
    "PIDS_C": obd.commands.PIDS_C,
    "STATUS_DRIVE_CYCLE": obd.commands.STATUS_DRIVE_CYCLE,
    "CONTROL_MODULE_VOLTAGE": obd.commands.CONTROL_MODULE_VOLTAGE,
    "ABSOLUTE_LOAD": obd.commands.ABSOLUTE_LOAD,
    "COMMANDED_EQUIV_RATIO": obd.commands.COMMANDED_EQUIV_RATIO,
    "RELATIVE_THROTTLE_POS": obd.commands.RELATIVE_THROTTLE_POS,
    "AMBIANT_AIR_TEMP": obd.commands.AMBIANT_AIR_TEMP,
    "THROTTLE_POS_B": obd.commands.THROTTLE_POS_B,
    "THROTTLE_POS_C": obd.commands.THROTTLE_POS_C,
    "ACCELERATOR_POS_D": obd.commands.ACCELERATOR_POS_D,
    "ACCELERATOR_POS_E": obd.commands.ACCELERATOR_POS_E,
    "ACCELERATOR_POS_F": obd.commands.ACCELERATOR_POS_F,
    "THROTTLE_ACTUATOR": obd.commands.THROTTLE_ACTUATOR,
    "RUN_TIME_MIL": obd.commands.RUN_TIME_MIL,
    "TIME_SINCE_DTC_CLEARED": obd.commands.TIME_SINCE_DTC_CLEARED,
    "MAX_MAF": obd.commands.MAX_MAF,
    "FUEL_TYPE": obd.commands.FUEL_TYPE,
    "ETHANOL_PERCENT": obd.commands.ETHANOL_PERCENT,
    "EVAP_VAPOR_PRESSURE_ABS": obd.commands.EVAP_VAPOR_PRESSURE_ABS,
    "EVAP_VAPOR_PRESSURE_ALT": obd.commands.EVAP_VAPOR_PRESSURE_ALT,
    "SHORT_O2_TRIM_B1": obd.commands.SHORT_O2_TRIM_B1,
    "LONG_O2_TRIM_B1": obd.commands.LONG_O2_TRIM_B1,
    "SHORT_O2_TRIM_B2": obd.commands.SHORT_O2_TRIM_B2,
    "LONG_O2_TRIM_B2": obd.commands.LONG_O2_TRIM_B2,
    "FUEL_RAIL_PRESSURE_ABS": obd.commands.FUEL_RAIL_PRESSURE_ABS,
    "RELATIVE_ACCEL_POS": obd.commands.RELATIVE_ACCEL_POS,
    "HYBRID_BATTERY_REMAINING": obd.commands.HYBRID_BATTERY_REMAINING,
    "OIL_TEMP": obd.commands.OIL_TEMP,
    "FUEL_INJECT_TIMING": obd.commands.FUEL_INJECT_TIMING,
    "FUEL_RATE": obd.commands.FUEL_RATE,
}

# Activate the logger to send log entries to app.viam.com, visible under the logs tab
LOGGER = getLogger(__name__)

# Model Family & Name
MODULENAMESPACE = "jeep"
MODULETYPE = "component"
MODULENAME = "movement_sensor"

class OBDII(MovementSensor):
    """
    Class representing the sensor to be implemented/wrapped.
    Subclass the Viam Movement Sensor component and implement the required functions
    """

    MODEL: ClassVar[Model] = Model(ModelFamily(MODULENAMESPACE, MODULETYPE), MODULENAME)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        Validates the configuration added to the Viam RDK and executed before new(). 
        Implement any specific attribute validation required by your component.
        """
        if "cmd" in config.attributes.fields:
            if not config.attributes.fields["cmd"].HasField("list_value"):
                raise ValueError("Command must be a list.")
            command = config.attributes.fields["cmd"].list_value
            if command == []:
                raise ValueError("Command cannot be an empty list.")
        return []

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """
        This constructor instantiates a new "OBDII" component based upon the 
        configuration added to the RDK.
        """
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    def __init__(self, name: str):
        """
        Actual component instance constructor
        """
        super().__init__(name)
        self.command = []

        # Connect to the OBD-II device
        self.connection = obd.OBD("/dev/ttyUSB0")

        # Check if the connection was successful
        if self.connection.is_connected():
            print("Connected to OBD-II interface")
        else:
            print("Failed to connect to OBD-II interface")

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
        This method is executed whenever a new mysensor instance is created or
        configuration attributes are changed
        """
        self.command = obd_commands.keys()

    async def close(self):
        """
        Optional function to include. This will be called when the resource
        is removed from the config or the module is shutting down.
        """
        LOGGER.info("%s is closed.", self.name)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        """
        Optional general purpose method to be used for additional
        device specific operations e.g. reseting a sensor.
        """
        raise NotImplementedError()

    async def get_readings(
        self, extra: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Mapping[str, Any]:
        response: Mapping[str, Any] = {}
        for cmd in self.command:
            reading = None
            obd_cmd = obd_commands.get(cmd)
            if obd_cmd is not None:
                try:
                    reading = self.connection.query(obd_cmd)
                    if reading.value is not None:
                        parsed = None
                        try:
                            parsed = quantity_to_array(reading.Value)
                        except:
                            parsed = reading.Value
                        response[cmd] = parsed
                except:
                    pass
            else:
                response[cmd] = "invalid_cmd"
        return response
    
    async def get_position(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Tuple[GeoPoint, float]:
        return GeoPoint(latitude=0.0, longitude=0.0), 0.0

    async def get_linear_velocity(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Vector3:
        return Vector3(x=0.0, y=0.0, z=0.0)

    async def get_angular_velocity(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Vector3:
        return Vector3(x=0.0, y=0.0, z=0.0)

    async def get_linear_acceleration(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Vector3:
        return Vector3(x=0.0, y=0.0, z=0.0)

    async def get_compass_heading(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> float:
        return 0.0

    async def get_orientation(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Orientation:
        return Orientation(o_x=0.0, o_y=0.0, o_z=0.0, theta=0.0)

    async def get_properties(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Dict[str, Any]:
        return {"property1": "value1", "property2": "value2"}

    async def get_accuracy(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> Dict[str, Any]:
        return {"accuracy1": 0.0, "accuracy2": 0.0}

    async def get_geometries(
        self, *, extra: Dict[str, Any] = None, timeout: float = None, **kwargs
    ) -> List[Geometry]:
        return [Geometry(center=GeoPoint(latitude=0.0, longitude=0.0), radius=1.0)]

    @classmethod
    def from_robot(cls, robot: Any, name: str) -> 'DummyMovementSensorClient':
        return cls(name)

    @classmethod
    def get_resource_name(cls, name: str) -> str:
        return f"resource_{name}"

    def get_operation(self, kwargs: Mapping[str, Any]) -> str:
        return "dummy_operation"

# Register this model with the module.
Registry.register_resource_creator(
    MovementSensor.SUBTYPE,
    OBDII.MODEL,
    ResourceCreatorRegistration(OBDII.new, OBDII.validate_config),
)