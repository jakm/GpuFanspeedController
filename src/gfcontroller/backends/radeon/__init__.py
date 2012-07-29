#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import re
import shlex
import subprocess

from gfcontroller.backends import BackendError
from gfcontroller.backends.base import GpuBackend

class RadeonBackend(GpuBackend):
    def __init__(self, device_id, device_name=None):
        self._device_id = int(device_id)
        self._device_name = device_name if device_name else str(device_id)

        self.__get_fanspeed_cmd = shlex.split('aticonfig --pplib-cmd "get fanspeed %d"' % self._device_id)
        self.__set_fanspeed_cmd = shlex.split('aticonfig --pplib-cmd "set fanspeed %d %%d"' % self._device_id)
        self.__get_temperature_cmd = shlex.split('aticonfig --adapter=%d --od-gettemperature' % self._device_id)
        
        #=======================================================================
        # EXAMPLE OF OUTPUT:
        # Adapter 0 - AMD Radeon HD 6800 Series  
        #    Sensor 0: Temperature - 35.00 C
        #=======================================================================
        self.__get_temperature_re = re.compile(r'^Adapter %d.+\n.+Temperature - (\d?\d?\d.\d\d) C$' % self._device_id)
        #=======================================================================
        # EXAMPLE OF OUTPUT:
        # Fan speed query: 
        #    Query Index: 0, Speed in percent
        #    Result: Fan Speed: 73%
        #=======================================================================
        self.__get_fanspeed_re = re.compile(r'^Fan speed query:.*\n.*Query Index: %d.+\n.+Fan Speed: (\d?\d?\d)%%$' % self._device_id)

    @property
    def device_name(self):
        return self._device_name
    
    def _get_fanspeed(self):
        returned_data = self.__exec_cmd(self.__get_fanspeed_cmd)
        if returned_data[0] == 0:
            match = self.__get_fanspeed_re.match(returned_data[1])
            if match:
                return int(match.groups()[0])
            else:
                msg = 'Error when getting actual fanspeed of adapter %s' % self.device_name
                msg += "; DEBUG: Regular expression = r'" + self.__get_fanspeed_re.pattern + "'"
                msg += "; DEBUG: Aticonfig output = '" + returned_data[1] + "'"
                raise BackendError(msg)
                
        else:
            self.__cmd_fail(returned_data)
    
    def _set_fanspeed(self, value):
        if not (0 < value <= 100):
            raise ValueError('Correct value of speed is between 0 and 100 %%, value %d was given.' % (value,))

        args = self.__get_args_with_fanspeed(value)
        returned_data = self.__exec_cmd(args)
        if returned_data[0] != 0:
            self.__cmd_fail(returned_data)
    
    fanspeed = property(_get_fanspeed, _set_fanspeed)
    
    @property
    def temperature(self):
        returned_data = self.__exec_cmd(self.__get_temperature_cmd)
        if returned_data[0] == 0:
            match = self.__get_temperature_re.match(returned_data[1])
            if match:
                return int(float(match.groups()[0]))
            else:
                msg = 'Error when getting actual temperature of adapter %s' % self.device_name
                msg += "; DEBUG: Regular expression = r'" + self.__get_temperature_re.pattern + "'"
                msg += "; DEBUG: Aticonfig output = '" + returned_data[1] + "'"
                raise BackendError(msg)
        else:
            self.__cmd_fail(returned_data)
    
    def __exec_cmd(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        stdout = process.stdout.read().decode('utf8').strip()
        stderr = process.stderr.read().decode('utf8').strip()
        return (process.returncode, stdout, stderr)
    
    def __cmd_fail(self, returned_data):
        raise BackendError('Aticonfig exited with code %d:\n%s\n\n' % (returned_data[0], returned_data[2]))
    
    def __get_args_with_fanspeed(self, value):
        args = list(self.__set_fanspeed_cmd)
        args[-1] %= value # set fanspeed to last arg
        return args