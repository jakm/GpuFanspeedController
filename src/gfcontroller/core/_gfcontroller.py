#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

from gfcontroller.backends.base import GpuBackend

CRITICAL_SPEED = 100
MAX_SPEED = 70

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
            new_speed = actual_speed + speed_increment
        elif self._critical_temp <= actual_temp:
            new_speed = MAX_SPEED
        
        self._backend.fanspeed = new_speed
        
        self._last_temp = actual_temp
