"""
A basic example of how to wrap a sensor into the Viam sensor component in Python
"""

from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence

from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes


import obd

obdCommand = {
    "STATUS": obd.commands.STATUS,
    "FUEL_STATUS": obd.commands.FUEL_STATUS,
    "ENGINE_LOAD": obd.commands.ENGINE_LOAD,
    "COOLANT_TEMP": obd.commands.COOLANT_TEMP,
    "OIL_TEMP": obd.commands.OIL_TEMP,
    "RPM": obd.commands.RPM,
    "SPEED": obd.commands.SPEED,
}

# Activate the logger to send log entries to app.viam.com, visible under the logs tab
LOGGER = getLogger(__name__)

# Model Family & Name
MODULENAMESPACE = "maxhorowitz"
MODULETYPE = "utils"
MODULENAME = "obdii"

class OBDII(Sensor):
    """
    Class representing the sensor to be implemented/wrapped.
    Subclass the Viam Sensor component and implement the required functions
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
        self.command = ["RPM"]

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
        if "cmd" in config.attributes.fields:
            command = config.attributes.fields["cmd"].list_value
        else:
            command = ["RPM"]
        self.command = command

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
            obd_cmd = obdCommand.get(cmd)
            if obd_cmd is not None:
                reading = self.connection.query(obd_cmd)
                if reading.value is not None:
                    response[cmd] = reading.value
                else:
                    response[cmd] = "null"
            else:
                response[cmd] = "invalid_cmd"
        return response


# Register this model with the module.
Registry.register_resource_creator(
    Sensor.SUBTYPE,
    OBDII.MODEL,
    ResourceCreatorRegistration(OBDII.new, OBDII.validate_config),
)
