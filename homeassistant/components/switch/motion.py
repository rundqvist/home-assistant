"""
Support for Motion switches.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.motion/
"""
import logging

import voluptuous as vol

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_COMMAND_ON, CONF_COMMAND_OFF)
from homeassistant.components import motion
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['motion']
DOMAIN = 'motion'


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Motion switch platform."""
    
    motion_data = hass.data[DOMAIN]

    switches = []

    for camera in motion_data['cameras']:

        if camera['config']['camera_name'] != None:
            name = camera['config']['camera_name']
        else:
            name = 'Motion Camera {}'.format(str(camera['id']))

        switches.append(
            MotionSwitch(
                camera['id'],
                name
            )
        )

    add_entities(switches)


class MotionSwitch(SwitchDevice):
    """Representation of a Motion switch."""

    icon = 'mdi:record-rec'

    def __init__(self, monitor_id, monitor_name):
        """Initialize the switch."""
        self._monitor_id = monitor_id
        self._monitor_name = monitor_name
        self._state = motion.is_on(self._monitor_id)

    @property
    def name(self):
        """Return the name of the switch."""
        return "%s State" % self._monitor_name

    def update(self):
        """Update the switch value."""
        
        self._state = motion.is_on(self._monitor_id)

    @property
    def is_on(self):
        """Return True if entity is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        motion.turn_on(self._monitor_id)

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        motion.turn_off(self._monitor_id)
