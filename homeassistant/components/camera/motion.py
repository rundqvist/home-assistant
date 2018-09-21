"""
Support for Motion camera streaming.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/camera.motion/
"""
import asyncio
import logging
import requests
from urllib.parse import urljoin, urlencode

from homeassistant.const import CONF_NAME
from homeassistant.components.camera.mjpeg import (
    CONF_MJPEG_URL, MjpegCamera)

from homeassistant.components import motion

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['motion']
DOMAIN = 'motion'


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_entities,
                         discovery_info=None):
    """Set up the Motion cameras."""

    _LOGGER.error("async_setup_platform")

    motion_data = hass.data[DOMAIN]

    cameras = []

    for camera in motion_data['cameras']:
        _LOGGER.error("Setting up camera id: {}".format(camera['id']))

        if camera['config']['camera_name'] != None:
            name = camera['config']['camera_name']
        else:
            name = 'Motion Camera {}'.format(str(camera['id']))

        device_info = {
            CONF_NAME: name,
            CONF_MJPEG_URL: '{}:{}'.format(motion_data['hosturl'], camera['config']['stream_port'])
        }
        cameras.append(MotionCamera(hass, device_info, camera))

    async_add_entities(cameras)


class MotionCamera(MjpegCamera):
    """Representation of a Motion camera Stream."""

    def __init__(self, hass, device_info, camera):
        """Initialize as a subclass of MjpegCamera."""
        super().__init__(hass, device_info)
        self._monitor_id = camera['id']
        self._is_recording = motion.is_on(self._monitor_id)

    @property
    def should_poll(self):
        """Update the recording state periodically."""
        return True

    def update(self):
        """Update our recording state from Motion."""

        self._is_recording = motion.is_on(self._monitor_id)

    @property
    def is_recording(self):
        """Return whether the monitor has motion detection activated."""
        return self._is_recording
