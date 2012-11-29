#!/usr/bin/env python3

from distutils.core import setup

setup(name='GpuFanspeedController',
      version='0.2',
      description=('Simple daemon to control GPU fan '
                   'speed depending on temperature.'),
      author='Jakub Matys',
      author_email='matys.jakub@gmial.com',
      license='BSD',
      url='https://github.com/jakm/GpuFanspeedController',
      install_requires=['python>=3.0'],
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
                  ('/etc/systemd/system', ['gfcontroller.service'])]
)
