#Copyright (c) 2012, Jakub Matys <matys.jakub@gmail.com>
#All rights reserved.

import io
import logging
import traceback

import gfcontroller.daemon

CONFIGFILE = 'gfcontroller.cfg'

def main():
    try:
        daemon = gfcontroller.daemon.Daemon(CONFIGFILE)
        daemon.start_deamon()
    except gfcontroller.daemon.DaemonError as e:
        logging.error(str(e))
    except Exception as e:
        msg = 'Unhandled exception occured: ' + str(e)
        logging.error(msg)
        buf = io.StringIO()
        traceback.print_exc(file=buf)
        logging.error(buf.getvalue())

if __name__ == '__main__':
    main()