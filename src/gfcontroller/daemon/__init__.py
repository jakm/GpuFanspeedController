#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

# TODO: reimplement with systemd

import configparser
import logging
import sys
import time

import gfcontroller.backends
import gfcontroller.core

LOGGER = logging.getLogger('daemon')

class DaemonError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Daemon:
    _DAEMON_SECTION = 'Daemon'
    _DEVICE_SECTION = 'Device'
    _SLEEP_OPTION = 'sleep'
    _DEBUG_OPTION = 'debug'
    _NAME_OPTION = 'name'
    _BACKEND_OPTION = 'backend'
    _MIN_SPEED_OPTION = 'min_speed'
    _LIMIT_TEMP_OPTION = 'limit_temp'
    _CRITICAL_TEMP_OPTION = 'critical_temp'
    
    def __init__(self, configfile):
        self.config = configparser.ConfigParser()
        self.config.read(configfile)

    def start_deamon(self):
        controllers, sleep = self.__setup()
        
        while(True):
            for controller in controllers:
                controller.control()
            
            LOGGER.debug('Going sleep')
            time.sleep(sleep)
    
    def __setup(self):
        if not self.config.has_section(self._DAEMON_SECTION):
            raise DaemonError('No Daemon section in config file.')
        
        if len(section for section in self.config.sections() if section.startswith(self._DEVICE_SECTION)) == 0:
            raise DaemonError('No Device section in config file.')
        
        if (self.config.has_option(self._DAEMON_SECTION, self._DEBUG_OPTION)
            and self.config.getboolean(self._DAEMON_SECTION, self._DEBUG_OPTION)):
            logging.root.setLevel(logging.DEBUG)
        
        if not self.config.has_option(self._DAEMON_SECTION, self._SLEEP_OPTION):
            raise DaemonError("Daemon section doesn't contain sleep option.")
        
        sleep = self.config.getint(self._DAEMON_SECTION, self._SLEEP_OPTION)
        
        if sleep <= 0:
            raise DaemonError('Invalid value of sleep option. Use integer > 0.')
        
        LOGGER.debug('Sleep interval: ' + sleep)
        
        controllers = self.__get_controllers()
        
        return controllers, sleep
    
    def __get_controllers(self):
        controllers = []
        
        for section in self.config.sections():
            if section == self._DAEMON_SECTION:
                continue
            
            tmp = section.split(':')
            if len(tmp) != 2:
                raise DaemonError('Error when parsing device device_id in section %s.' % (section,))
            
            device_id = tmp[1].trim()
            
            device_name = None
            if self.config.has_option(section, self._NAME_OPTION):
                device_name = self.config.has_option(section, self._NAME_OPTION)
            
            for option in (self._BACKEND_OPTION, self._MIN_SPEED_OPTION, self._LIMIT_TEMP_OPTION, self._CRITICAL_TEMP_OPTION):
                if not self.config.has_option(section, option):
                    raise DaemonError("Device section %s doesn't contain %s option." %(section, option))
            
            backend_name = self.config.get(section, self._BACKEND_OPTION)
            if backend_name not in gfcontroller.backends.NAMES.keys():
                raise DaemonError('Backend named %s is not defined.' % (backend_name,))
            
            backend_module, backend_class = gfcontroller.backends.NAMES[backend_name].split('.')
            backend_module = 'gfcontroller.backends.' + backend_module
            backend = self.__load_backend(backend_module, backend_class)
            
            min_speed = self.config.getint(section, self._MIN_SPEED_OPTION)
            limit_temp = self.config.getint(section, self._LIMIT_TEMP_OPTION)
            critical_temp = self.config.getint(section, self._CRITICAL_TEMP_OPTION)
            
            controller = gfcontroller.core.GpuFanspeedController(backend(device_id, device_name))
            controller.initialize(min_speed, limit_temp, critical_temp)
            
            controllers.append(controller)
            
            LOGGER.debug('Added device: id=%s, backend=%s, min_speed=%s, limit_temp=%s, critical_temp=%s' %
                         (device_id, backend_name, min_speed, limit_temp, critical_temp))
        
        return controllers
    
    def __load_backend(self, module_name, class_name):
        if module_name in sys.modules.keys():
            module = sys.modules[module_name]
        else:
            module = __import__(module_name)
        
        return self.__get_class(module, class_name)
    
    def __get_class(self, module, class_name):
        cls = self.__get_class.cache.get((module, class_name), None)
        if cls is None:
            try:
                cls = getattr(module, class_name)
                if type(cls) is not type(object):
                    raise AttributeError
                self.__get_class.cache[module, class_name] = cls
            except AttributeError:
                raise DaemonError("Module %s doesn't contain class %s" % (module.__name__, class_name))
            return cls
    __get_class.cache = {}