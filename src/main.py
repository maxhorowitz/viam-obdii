"""
A basic example of how to wrap a sensor into the Viam sensor component in Python
"""

import asyncio

from viam.module.module import Module
from viam.components.movement_sensor import MovementSensor
from viam.resource.registry import Registry, ResourceCreatorRegistration

from movement_sensor.obdii import OBDII


async def main():
    """
    This function creates and starts a new module and verifies that the required 
    models are properly registered -> see my_sensor.py at the end of the file.
    """

    module = Module.from_args()
    module.add_model_from_registry(MovementSensor.SUBTYPE, OBDII.MODEL)
    await module.start()

if __name__ == "__main__":
    asyncio.run(main())
