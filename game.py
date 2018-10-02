#!/usr/bin/env python3
# coding=utf-8
import src.system as internal
from src.core import Application
from datetime import datetime

import logging
Log = logging.getLogger('MainLogger')

def main(debug):
    app = Application(debug)

if __name__ == '__main__':
    parser = internal.configure_argparser()
    args = parser.parse_args()
    internal.define_loggable_exceptions()
    internal.configure_logger(args.verbose)
    time_start = datetime.now()
    Log.info('Starting script ({})'.format(time_start))
    main(args.debug)
    time_end = datetime.now()
    drt = time_end - time_start
    secs = drt.seconds%60
    mins = str(int(drt.seconds//60))
    secs = '0'+str(secs) if secs < 10 else str(secs)
    Log.info('Run time: {}:{}'.format(mins, secs))
