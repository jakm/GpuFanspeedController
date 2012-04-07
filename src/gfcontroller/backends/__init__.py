#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

NAMES = {
#    NAME: 'submodule.class'
    'RADEON': 'radeon.RadeonBackend',
#    'NVIDIA': 'nvidia.NvidiaBackend',
    'TEST': 'test.TestBackend'
    }

class BackendError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)