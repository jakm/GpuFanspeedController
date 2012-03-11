#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import shlex
import subprocess

from gfcontroller.backends.base import GpuBackend

class RadeonBackend(GpuBackend):
    def __init__(self, device_id, device_name=None):
        self._device_id = device_id
        self._device_name = device_name if device_name else device_id

        self.__get_fanspeed_cmd = shlex.split('aticonfig --pplib-cmd "get fanspeed %d"' % self._device_id)
        self.__set_fanspeed_cmd = shlex.split('aticonfig --pplib_cmd "set fanspeed %d %%d"' % self._device_id)
        self.__get_temperature_cmd = shlex.split('aticonfig --adapter=%d --od-gettemperature' % self._device_id)

    @property
    def device_name(self):
        return self._device_name
    
    def _get_fanspeed(self):
        returned_data = self.__exec_cmd(self.__get_fanspeed_cmd)
        if returned_data[0] == 0:
            pass # TODO regexp
        else:
            pass # TODO raiserror
    
    def _set_fanspeed(self, value):
        if not (0 < value <= 100):
            raise ValueError('Use value of speed between 0 and 100 %')

        returned_data = self.__exec_cmd(self.__set_fanspeed_cmd % value)
        if returned_data[0] != 0:
            pass # TODO raiserror
    
    fanspeed = property(_get_fanspeed, _set_fanspeed)
    
    @property
    def temperature(self):
        returned_data = self.__exec_cmd(self.__get_fanspeed_cmd)
        if returned_data[0] == 0:
            pass # TODO regexp
        else:
            pass # TODO raiserror
    
    def __exec_cmd(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        return (p.returncode, p.stdout.readlines(), p.stderr.readlines())
