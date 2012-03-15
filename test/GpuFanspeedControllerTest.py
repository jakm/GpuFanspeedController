#!/usr/bin/env python3

#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import os
import sys
import tempfile

CONFIG = '''
[Daemon]
sleep=10
debug=true

[Device:0]
name=TEST1
backend=TEST
min_speed=40
limit_temp=39
critical_temp=60

#[Device:1]
#name=TEST2
#backend=TEST
#min_speed=40
#limit_temp=39
#critical_temp=60
'''

def run_test():
    with tempfile.NamedTemporaryFile() as f:
        f.write(CONFIG.encode())
        f.flush()
        try:
            GpuFanspeedController.CONFIGFILE = f.name
            GpuFanspeedController.main()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    cwd = os.path.abspath(os.path.basename(sys.argv[0]))
    srcdir = os.path.normpath(os.path.join(cwd, '..', 'src'))
    sys.path.insert(0, srcdir)
    
    import GpuFanspeedController
    
    run_test()
        