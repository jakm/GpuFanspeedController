#!/usr/bin/env python3

#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import sys
from distutils.core import setup
from distutils.command.install import install
from distutils.errors import DistutilsPlatformError


class _install(install):
    def run(self):
        try:
            major = sys.version_info.major
        except AttributeError:
            major = 0

        if major < 3:
            raise DistutilsPlatformError('Use Python 3.0 or above')

        super(_install, self).run()


setup(name='GpuFanspeedController',
      version='0.2',
      description=('Simple daemon to control GPU fan '
                   'speed depending on temperature.'),
      author='Jakub Matys',
      author_email='matys.jakub@gmail.com',
      license='BSD',
      url='https://github.com/jakm/GpuFanspeedController',
      packages=['gfcontroller',
                'gfcontroller.backends',
                'gfcontroller.backends.base',
                'gfcontroller.backends.nvidia',
                'gfcontroller.backends.radeon',
                'gfcontroller.backends.test',
                'gfcontroller.core'],
      package_dir={'': 'src'},
      scripts=['src/GpuFanspeedController'],
      data_files=[('/etc', ['gfcontroller.cfg.sample']),
                  ('/etc/systemd/system', ['gfcontroller.service'])],
      cmdclass={'install': _install})
