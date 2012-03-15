#!/usr/bin/env python3

#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import configparser
import io
import logging
import sys
import time
import traceback

import gfcontroller.backends.base
import gfcontroller.core

LOGGER = logging.getLogger('daemon')

CONFIGFILE = '/etc/gfcontroller.cfg'

DAEMON_SECTION = 'Daemon'
DEVICE_SECTION = 'Device'
SLEEP_OPTION = 'sleep'
DEBUG_OPTION = 'debug'
NAME_OPTION = 'name'
BACKEND_OPTION = 'backend'
MIN_SPEED_OPTION = 'min_speed'
LIMIT_TEMP_OPTION = 'limit_temp'
CRITICAL_TEMP_OPTION = 'critical_temp'

class DaemonError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def start_deamon():
    controllers, sleep = setup()
    LOGGER.debug('Main loop')
    LOGGER.debug('='*30)
    
    while(True):
        for controller in controllers:
            controller.control()
        
        LOGGER.debug('Going sleep')
        LOGGER.debug('='*30)
        time.sleep(sleep)

def setup():
    config = configparser.ConfigParser()
    config.read(CONFIGFILE)
    
    if not config.has_section(DAEMON_SECTION):
        raise DaemonError('No Daemon section in config file.')
    
    if len([section for section in config.sections() if section.startswith(DEVICE_SECTION)]) == 0:
        raise DaemonError('No Device section in config file.')
    
    if (config.has_option(DAEMON_SECTION, DEBUG_OPTION) and config.getboolean(DAEMON_SECTION, DEBUG_OPTION)):
        logging.root.setLevel(logging.DEBUG)
    
    if not config.has_option(DAEMON_SECTION, SLEEP_OPTION):
        raise DaemonError("Daemon section doesn't contain sleep option.")
    
    sleep = config.getint(DAEMON_SECTION, SLEEP_OPTION)
    
    if sleep <= 0:
        raise DaemonError('Invalid value of sleep option. Use integer > 0.')
    
    LOGGER.debug('Sleep interval: ' + str(sleep))
    LOGGER.debug('-'*30)
    
    controllers = get_controllers(config)
    
    return controllers, sleep

def get_controllers(config):
    controllers = []
    
    for section in config.sections():
        if section == DAEMON_SECTION:
            continue
        
        LOGGER.debug('Setting up section %s' %(section,))
        
        tmp = section.split(':')
        if len(tmp) != 2:
            raise DaemonError('Error when parsing device device_id in section %s.' % (section,))
        
        device_id = tmp[1].strip()
        
        device_name = None
        if config.has_option(section, NAME_OPTION):
            device_name = config.has_option(section, NAME_OPTION)
        
        for option in (BACKEND_OPTION, MIN_SPEED_OPTION, LIMIT_TEMP_OPTION, CRITICAL_TEMP_OPTION):
            if not config.has_option(section, option):
                raise DaemonError("Device section %s doesn't contain %s option." %(section, option))
        
        backend_name = config.get(section, BACKEND_OPTION)
        if backend_name not in gfcontroller.backends.NAMES.keys():
            raise DaemonError('Backend named %s is not defined.' % (backend_name,))
        
        backend_module, backend_class = gfcontroller.backends.NAMES[backend_name].split('.')
        backend_module = 'gfcontroller.backends.' + backend_module
        backend = load_backend(backend_module, backend_class)
        
        min_speed = config.getint(section, MIN_SPEED_OPTION)
        limit_temp = config.getint(section, LIMIT_TEMP_OPTION)
        critical_temp = config.getint(section, CRITICAL_TEMP_OPTION)
        
        controller = gfcontroller.core.GpuFanspeedController(backend(device_id, device_name))
        controller.initialize(min_speed, limit_temp, critical_temp)
        
        controllers.append(controller)
        
        LOGGER.debug('Added device: id=%s, backend=%s, min_speed=%s, limit_temp=%s, critical_temp=%s' %
                     (device_id, repr(backend), min_speed, limit_temp, critical_temp))
    
    return controllers

def load_backend(module_name, class_name):
    if not module_name in sys.modules.keys():
        __import__(module_name)
    
    module = sys.modules[module_name]
    
    return get_class(module, class_name)

def get_class(module, class_name):
    LOGGER.debug('Loading class %s in module %s' % (class_name, module.__name__))
    cls = get_class.cache.get((module, class_name), None)
    if cls is None:
        try:
            cls = getattr(module, class_name)
            if not issubclass(cls, gfcontroller.backends.base.GpuBackend):
                raise DaemonError("Class %s is not subclass of GpuBackend" % (class_name,))
            get_class.cache[module, class_name] = cls
        except AttributeError:
            raise DaemonError("Module %s doesn't contain class %s" % (module.__name__, class_name))
    return cls
get_class.cache = {}

def main():
    try:
        start_deamon()
    except DaemonError as e:
        logging.error(str(e))
    except Exception as e:
        msg = 'Unhandled exception occured: ' + str(e)
        logging.error(msg)
        buf = io.StringIO()
        traceback.print_exc(file=buf)
        logging.error(buf.getvalue())

if __name__ == '__main__':
    main()