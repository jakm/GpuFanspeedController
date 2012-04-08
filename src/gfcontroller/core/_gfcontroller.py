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
    
    def initialize(self, min_speed, limit_temp, critical_temp):
        self._min_speed = min_speed
        self._limit_temp = limit_temp
        self._critical_temp = critical_temp
        
        self._temp_to_speed_ratio = (MAX_SPEED - self._min_speed) / (self._critical_temp - self._limit_temp)
        
        self._last_temp = self._backend.temperature
        
        LOGGER.debug('Controller initialized')
    
    @property
    def min_speed(self):
        return self._min_speed
    
    @property
    def limit_temp(self):
        return self._limit_temp
    
    @property
    def critical_temp(self):
        return self._critical_temp

    def control(self):
        actual_temp = self._backend.temperature
        actual_speed = self._backend.fanspeed
        
        if actual_temp < self._limit_temp:
            new_speed = self._min_speed
        elif self._limit_temp <= actual_temp < self._critical_temp:
            temp_increment = (actual_temp * 100 / self._last_temp) - 100
            speed_increment = temp_increment * self._temp_to_speed_ratio
            
            # when temperature is increasing we will increase speed too
            # when temperature is stagnating or is descending we will keep speed until temperature will fall to limit
            new_speed = actual_speed + speed_increment if speed_increment > 0 else actual_speed
            
            # new_speed could be lower then _minspeed when _last_temp was lower then _limit_temp at initialization
            new_speed = self._min_speed if new_speed < self._min_speed else new_speed
        elif actual_temp >= self._critical_temp:
            new_speed = CRITICAL_SPEED
        
        self._backend.fanspeed = int(new_speed)
        
        self._last_temp = actual_temp
