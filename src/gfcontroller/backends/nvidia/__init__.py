#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

#===============================================================================
# THIS CODE IS STILL IN DEVELOPMENT
# DO NOT USE THIS BACKEND!!!
#===============================================================================

import re
import shlex
import subprocess

from gfcontroller.backends import BackendError
from gfcontroller.backends.base import GpuBackend

class NvidiaBackend(GpuBackend):
    def __init__(self, device_id, device_name=None):
        
        raise NotImplementedError('Backend is still in development!!!')
        
        self._device_id = int(device_id)
        self._device_name = device_name if device_name else str(device_id)

        self.__get_fanspeed_cmd = shlex.split('nvidia-settings -q [fan:%d]/GPUCurrentFanSpeed -t' % self._device_id)
        self.__set_fanspeed_cmd = shlex.split('nvidia-settings -a [gpu:%d]/GPUFanControlState=1 -a [fan:%d]/GPUCurrentFanSpeed=%%d' % self._device_id)
        self.__get_temperature_cmd = shlex.split('nvidia-settings -q [gpu:%d]/gpucoretemp -t' % self._device_id)

    @property
    def device_name(self):
        return self._device_name
    
    def _get_fanspeed(self):
        returned_data = self.__exec_cmd(self.__get_fanspeed_cmd)
        if returned_data[0] == 0:
            return int(returned_data[1])
        else:
            self.__cmd_fail(returned_data)
    
    def _set_fanspeed(self, value):
        if not (0 < value <= 100):
            raise ValueError('Use value of speed between 0 and 100 %')
        
        args = self.__get_args_with_fanspeed(value)
        returned_data = self.__exec_cmd(args)
        if returned_data[0] != 0:
            self.__cmd_fail(returned_data)
    
    fanspeed = property(_get_fanspeed, _set_fanspeed)
    
    @property
    def temperature(self):
        returned_data = self.__exec_cmd(self.__get_fanspeed_cmd)
        if returned_data[0] == 0:
            return int(returned_data[1])
        else:
            self.__cmd_fail(returned_data)
    
    def __exec_cmd(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        stdout = p.stdout.read().decode('utf8').strip()
        stderr = p.stderr.read().decode('utf8').strip()
        return (p.returncode, stdout, stderr)
    
    def __cmd_fail(self, returned_data):
        raise BackendError('nvidia-settings exited with code %d:\n%s\n\n' % (returned_data[0], returned_data[2]))
    
    def __get_args_with_fanspeed(self, value):
        args = list(self.__set_fanspeed_cmd)
        args[-1] %= value # set fanspeed to last arg
        return args