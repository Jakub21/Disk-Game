#!/usr/bin/env python3
# coding=utf-8
from datetime import datetime
import src.system as internal
from src.launcher import Launcher
from src.core import Application

import logging
Log = logging.getLogger('MainLogger')

def main(debug):
    while True:
        launcher = Launcher(debug)
        while not launcher.leaving:
            launcher.loop()
            if launcher.starting_game:
                launcher.quit()
                break
        else: break
        if launcher.starting_game:
            game = Application(launcher)
            del launcher
            while not game.leaving:
                game.loop()
            game.cleanup()
            if not game.back_to_launcher:
                break
            del game

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
