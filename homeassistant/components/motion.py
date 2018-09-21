"""
Support for Motion.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/motion/
"""
import logging
from urllib.parse import urljoin

import requests
import voluptuous as vol

from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_PATH, CONF_SSL, CONF_USERNAME,
    CONF_VERIFY_SSL)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 7999
DEFAULT_SSL = False
DEFAULT_TIMEOUT = 10
DEFAULT_VERIFY_SSL = True
DOMAIN = 'motion'

MOTION = {}

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.positive_int,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Motion component."""
    global MOTION
    MOTION = {}

    conf = config[DOMAIN]
    if conf[CONF_SSL]:
        schema = 'https'
    else:
        schema = 'http'

    username = conf.get(CONF_USERNAME, None)
    password = conf.get(CONF_PASSWORD, None)

    ssl_verification = conf.get(CONF_VERIFY_SSL)

    MOTION['hosturl'] = '{}://{}'.format(schema, conf[CONF_HOST])
    MOTION['apiurl'] = '{}://{}:{}'.format(schema, conf[CONF_HOST], conf[CONF_PORT])
    MOTION['username'] = username
    MOTION['password'] = password
    MOTION['ssl_verification'] = ssl_verification

    hass.data[DOMAIN] = MOTION

    return connect()


def connect():
    # """Connect to Motion."""

    try:
        req = requests.get(MOTION['apiurl'], timeout=DEFAULT_TIMEOUT)
    except:
         _LOGGER.error("Could not connect to Motion at {}".format(MOTION['apiurl']))
         return False

    lines = req.text.splitlines()

    if not lines[0].startswith("Motion"):
        _LOGGER.error("Motion is not found at {}".format(MOTION['apiurl']))
        return False

    cameras = []

    for line in lines:

        if line.isdigit() and line != '0':
            
            cfg = get_config(int(line))

            camera = {}
            camera['id'] = int(line)
            camera['config'] = cfg
            
            cameras.append(camera)

    MOTION['cameras'] = cameras

    return True


def is_on(id):
    """Check with Motion if swith is on."""
    
    url = urljoin(MOTION['apiurl'],"/%i/detection/status" % id)
    req = requests.get(url,timeout=DEFAULT_TIMEOUT)

    return req.text.find('ACTIVE') > 0


def turn_on(id):
    """Turn on switch."""

    _LOGGER.error("Switch turn on %i" % id)

    # http://localhost:7999/1/detection/start
    
    url = urljoin(MOTION['apiurl'],"/%i/detection/start" % id)
    req = requests.get(url,timeout=DEFAULT_TIMEOUT)

    return req.ok

def turn_off(id):
    """Turn off switch."""
    
    _LOGGER.error("Switch turn off %i" % id)

    url = urljoin(MOTION['apiurl'],"/%i/detection/pause" % id)
    req = requests.get(url,timeout=DEFAULT_TIMEOUT)

    return req.ok

def get_config(id):
    """Gets config by camera id"""
    
    url = urljoin(MOTION['apiurl'],"/%i/config/list" % id)
    r = requests.get(url)
    
    json = to_json(r.text)

    _LOGGER.error(json['target_dir'])

    return json

def to_json(text):
    """Converts motion config list to json"""
    json = {}
    lines = text.splitlines()

    for line in lines:
        parts = line.split(' = ', 1)

        if parts[1] == "(null)":
            json[parts[0]] = None
        else:
            json[parts[0]] = parts[1]

    return json