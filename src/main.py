"""
A basic example of how to wrap a sensor into the Viam sensor component in Python
"""

import asyncio

from viam.module.module import Module
from viam.components.sensor import Sensor

from sensor.my_sensor import MySensor


async def main():
    """
    This function creates and starts a new module, after adding all desired resource models.
    Resource models must be pre-registered -> see my_sensor.py at the end of the file.
    """
    module = Module.from_args()
    module.add_model_from_registry(Sensor.SUBTYPE, MySensor.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
