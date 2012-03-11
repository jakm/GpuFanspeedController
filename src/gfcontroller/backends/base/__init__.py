#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import abc

class GpuBackend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, device_id, device_name=None):
        raise NotImplementedError()
    
    @abc.abstractproperty
    def device_name(self):
        raise NotImplementedError()

    def _get_fanspeed(self):
        raise NotImplementedError()

    def _set_fanspeed(self, value):
        raise NotImplementedError()

    fanspeed = abc.abstractproperty(_get_fanspeed, _set_fanspeed)
    
    @abc.abstractproperty
    def temperature(self):
        raise NotImplementedError()
