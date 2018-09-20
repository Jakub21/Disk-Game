import numpy as np
import sys
import traceback as trb
import os
from argparse import ArgumentParser

import logging
Log = logging.getLogger('MainLogger')

def to_ns(input_dict):
    '''Converts dictionaries to namespaces'''
    class NameSpace:
        def __init__(self, input_dict):
            self.__dict__.update(input_dict)
    return NameSpace(input_dict)

def ifn_mkdir(directory):
    '''Creates directory, if it does not exist'''
    if not os.path.exists(directory):
        os.makedirs(directory)

def define_loggable_exceptions():
    '''Modifies system function that shows exception info'''
    def _excepthook(type, value, traceback):
        traceback = ''.join(trb.format_tb(traceback))
        m = 'An exception occurred:\n'+'-'*64+'\n'
        if len(traceback) > 0:
            m += 'Traceback (most recent call last):\n'+traceback+'\n'
        else:
            m += 'No traceback available\n'
        m += type.__name__+': '+str(value)
        m +='\n'+'-'*64+'\n'
        Log.error(m)
    sys.excepthook = _excepthook

def configure_logger(use_debug=False):
    '''Initializes logger with console handler'''
    level = logging.INFO
    if use_debug:
        level = logging.DEBUG
    Log.setLevel(level)
    formatter = '[%(asctime)s][%(filename)s:%(lineno)d] %(message)s'
    formatter = logging.Formatter(formatter, '%H:%M:%S')
    ConsoleHandler = logging.StreamHandler()
    ConsoleHandler.setLevel(level)
    ConsoleHandler.setFormatter(formatter)
    Log.addHandler(ConsoleHandler)

def configure_argparser():
    '''Creates and configures parser object'''
    parser = ArgumentParser('Editor')
    parser.add_argument('-v', '--verbose',
        help='Changes logging level to debug', action='store_true')
    return parser
