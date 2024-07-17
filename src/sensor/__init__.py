from viam.module.module import Module
from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration
from obdii import OBDII

# Register this model with the module.
Registry.register_resource_creator(
    Sensor.SUBTYPE,
    OBDII.MODEL,
    ResourceCreatorRegistration(OBDII.new, OBDII.validate_config),
)