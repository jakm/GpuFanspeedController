#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import logging
import random

from gfcontroller.backends.base import GpuBackend

DEFAULT_SPEED = 40
MIN_TEMP = 35
MAX_TEMP = 100

LOGGER = logging.getLogger('backends.test')

class TestBackend(GpuBackend):
    def __init__(self, device_id, device_name=None):
        self._device_id = device_id
        self._device_name = device_name if device_name else device_id
        
        self.__last_temp = MIN_TEMP
        self.__last_speed = DEFAULT_SPEED

    @property
    def device_name(self):
        return self._device_name
    
    def _get_fanspeed(self):
        return self.__last_speed
    
    def _set_fanspeed(self, value):
        if not (0 < value <= 100):
            raise ValueError('Use value of speed between 0 and 100 %')
        
        LOGGER.debug('Device: ' + self._device_id)
        LOGGER.debug('Called fanspeed propterty to set')
        LOGGER.debug('Last speed: ' + str(self.__last_speed))
        LOGGER.debug('Current speed: ' + str(value))
        #LOGGER.debug('-'*30)
        self.__last_speed = value
    
    fanspeed = property(_get_fanspeed, _set_fanspeed)
    
    @property
    def temperature(self):
        current_temp = random.randint(MIN_TEMP, MAX_TEMP)
        LOGGER.debug('Device: ' + self._device_id)
        LOGGER.debug('Called temperature property')
        LOGGER.debug('Last temp: ' + str(self.__last_temp))
        LOGGER.debug('Current temp: ' + str(current_temp))
        #LOGGER.debug('-'*30)
        self.__last_temp = current_temp
        return current_temp