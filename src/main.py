"""
A basic example of how to wrap a sensor into the Viam sensor component in Python
"""

import asyncio
from typing import Any, ClassVar, Dict, Mapping, Optional, Sequence

from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

# Activate the logger to send log entries to app.viam.com, visible under the logs tab
LOGGER = getLogger(__name__)


class MySensor(Sensor):
    """
    Class representing the sensor to be implemented/wrapped.
    Subclass the Viam Sensor component and implement the required functions
    """

    MODEL: ClassVar[Model] = Model(ModelFamily("sample", "sensor"), "mysensor")

    def __init__(self, name: str):
        super().__init__(name)
        self.multiplier = 1.0

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """
        This constructor instantiates a new "mysensor" component and
        executes the configuration/validation methods
        """
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        Implement provided component configuration attributes according to your needs
        """
        if "multiplier" in config.attributes.fields:
            if not config.attributes.fields["multiplier"].HasField("number_value"):
                raise ValueError("Multiplier must be a float.")
            multiplier = config.attributes.fields["multiplier"].number_value
            if multiplier == 0:
                raise ValueError("Multiplier cannot be 0.")
        return []

    async def get_readings(
        self, extra: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Mapping[str, Any]:
        """
        Required method to be implemented for a sensor component
        """
        return {"signal": 1 * self.multiplier}

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

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """
        This method is executed whenever a new mysensor instance is created or
        configuration attributes are changed
        """
        if "multiplier" in config.attributes.fields:
            multiplier = config.attributes.fields["multiplier"].number_value
        else:
            multiplier = 1.0
        self.multiplier = multiplier

    async def close(self):
        """
        Optional function to include. This will be called when the resource
        is removed from the config or the module is shutting down.
        """
        LOGGER.info("%s is closed.", self.name)


async def main():
    """
    This function creates and starts a new module, after adding all desired resource models.
    Resource creators must be registered before the module adds the resource model.
    """
    Registry.register_resource_creator(
        Sensor.SUBTYPE,
        MySensor.MODEL,
        ResourceCreatorRegistration(MySensor.new, MySensor.validate_config),
    )

    module = Module.from_args()
    module.add_model_from_registry(Sensor.SUBTYPE, MySensor.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
