#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import logging

from gfcontroller.backends.base import GpuBackend

CRITICAL_SPEED = 100
MAX_SPEED = 70

LOGGER = logging.getLogger('_gfcontroller')

class GpuFanspeedController:
    def __init__(self, backend):
        assert isinstance(backend, GpuBackend)

        self._backend = backend
        self._lowest_speed = None
        self._highest_speed = None
        self._lowest_temp = None
        self._highest_temp = None
        self._temp_to_speed_ratio = None
        self._last_temp = None
    
    def initialize(self, lowest_speed, highest_speed, lowest_temp, highest_temp):
        self._lowest_speed = lowest_speed
        self._highest_speed = highest_speed
        self._lowest_temp = lowest_temp
        self._highest_temp = highest_temp
        
        self._temp_to_speed_ratio = (self._highest_speed - self._lowest_speed) / (self._highest_temp - self._lowest_temp)
        
        self._last_temp = self._backend.temperature
        
        LOGGER.info('Controller initialized: lowest_speed = %d, highest_speed = %d, lowest_temp = %d, highest_temp = %d,'
                     ' temp_to_speed_ratio = %f, last_temp = %d'
                     % (self._lowest_speed, self._highest_speed, self._lowest_temp, self._highest_temp, 
                        self._temp_to_speed_ratio, self._last_temp))
    
    @property
    def lowest_speed(self):
        return self._lowest_speed
    
    @property
    def highest_speed(self):
        return self._highest_speed
    
    @property
    def lowest_temp(self):
        return self._lowest_temp
    
    @property
    def highest_temp(self):
        return self._highest_temp

    def control(self):
        actual_temp = self._backend.temperature
        actual_speed = self._backend.fanspeed
        
        if actual_temp < self._lowest_temp:
            new_speed = self._lowest_speed
        elif self._lowest_temp <= actual_temp <= self._highest_temp:
            temp_diff = actual_temp - self._lowest_temp
            new_speed = self._lowest_speed + self._temp_to_speed_ratio * temp_diff
        elif actual_temp > self._highest_temp:
            new_speed = CRITICAL_SPEED
        
        LOGGER.debug('Controlling: device = %s, last_temp = %d, last_speed = %d, actual_temp = %d, new_speed = %f'
                     % (self._backend.device_name, self._last_temp, actual_speed, actual_temp, new_speed))
        
        self._backend.fanspeed = int(new_speed)
        
        self._last_temp = actual_temp
