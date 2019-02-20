"""
Demo fan platform that has a fake fan.
For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import voluptuous as vol
from homeassistant.components.fan import (SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH,
                                          FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION, PLATFORM_SCHEMA)
from homeassistant.const import STATE_OFF
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_ID)
import homeassistant.helpers.config_validation as cv

FULL_SUPPORT = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
LIMITED_SUPPORT = SUPPORT_SET_SPEED

REQUIREMENTS = ['pytuya==7.0.2', 'pyaes==1.6.1']

CONF_DEVICE_ID = 'device_id'
CONF_LOCAL_KEY = 'local_key'

DEFAULT_ID = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Required(CONF_LOCAL_KEY): cv.string,
    vol.Optional(CONF_ID, default=DEFAULT_ID): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up of the Tuya switch."""
    import pytuya

    add_devices([TuyaLocalFan(
        pytuya.OutletDevice(
            config.get(CONF_DEVICE_ID),
            config.get(CONF_HOST),
            config.get(CONF_LOCAL_KEY),
        ),
        config.get(CONF_NAME),
        config.get(CONF_ID)
    )])

# def setup_platform(hass, config, add_entities_callback, discovery_info=None):
#    """Set up the demo fan platform."""
#    add_entities_callback([
#        DemoFan(hass, "Living Room Fan", FULL_SUPPORT),
#        DemoFan(hass, "Ceiling Fan", LIMITED_SUPPORT),
#    ])


class TuyaLocalFan(FanEntity):
    """A demonstration fan component."""

    # def __init__(self, hass, name: str, supported_features: int) -> None:
    def __init__(self, device, name, switchid):
        """Initialize the entity."""
        # self.hass = hass
        self._supported_features = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE
        self._speed = STATE_OFF
        self.oscillating = None
        # self.direction = None
        self._name = name
        self._device = device
        self._state = False
        # self._switchid = switchid
        self.oscillating = False

        # if supported_features & SUPPORT_OSCILLATE:
        # if supported_features & SUPPORT_DIRECTION:
        #    self.direction = "forward"

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def is_on(self):
        """Check if Tuya switch is on."""
        return self._state

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [STATE_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]
        # return ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the entity."""
        # if speed is None:
        #    speed = SPEED_MEDIUM
        # self.set_speed(speed)
        self._device.set_status(True, '1')
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self._device.set_status(False, '1')
        self._state = False
        self.schedule_update_ha_state()

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        self._speed = speed
        # self.schedule_update_ha_state()
        if speed == STATE_OFF:
            self._device.set_status(False, '1')
        elif speed == SPEED_LOW:
            self._device.set_status('4', '2')
        elif speed == SPEED_MEDIUM:
            self._device.set_status('8', '2')
        elif speed == SPEED_HIGH:
            self._device.set_status('12', '2')
        self.schedule_update_ha_state()

    # def set_direction(self, direction: str) -> None:
    #    """Set the direction of the fan."""
    #    self.direction = direction
    #    self.schedule_update_ha_state()

    def oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        self.oscillating = oscillating
        self._device.set_status(oscillating, '8')
        self.schedule_update_ha_state()

    # @property
    # def current_direction(self) -> str:
    #    """Fan direction."""
    #    return self.direction

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    def update(self):
        """Get state of Tuya switch."""
        success = False
        for i in range(3):
            if success is False:
                try:
                    status = self._device.status()
                    self._state = status['dps']['1']
                    if status['dps']['1'] == False:
                        self._speed = STATE_OFF
                    elif int(status['dps']['2']) <= 4:
                        self._speed = SPEED_LOW
                    elif int(status['dps']['2']) <= 8:
                        self._speed = SPEED_MEDIUM
                    elif int(status['dps']['2']) <= 12:
                        self._speed = SPEED_HIGH
                    # self._speed = status['dps']['2']
                    self.oscillating = status['dps']['8']
                    success = True
                except ConnectionError:
                    if i+1 == 3:
                        success = False
                        raise ConnectionError("Failed to update status.")
