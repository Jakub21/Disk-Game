import pygame as pg
from src.handlers import Handlers
from src.interface import Interface

import logging
Log = logging.getLogger('MainLogger')

class Application(Handlers, Interface):
    def __init__(self, launcher):
        Log.info('Starting game')
        self.leaving = False
        self.back_to_launcher = False
        self.extract_lnch(launcher)
        self.ui_init()
        self.handlers_init()
        self.begin()

    def loop(self):
        for evt in pg.event.get():
            self.evt_handle(evt)
        pg.display.update()
        if not self.session.is_paused:
            self.blit_full()

    def begin(self):
        self.session.begin()

    def extract_lnch(self, launcher):
        '''Extract variables from launcher that will be used in game'''
        self.CORE = launcher.CORE
        self.TEXT = launcher.TEXT
        self.CLRS = launcher.CLRS
        self.GAME = launcher.GAME
        self.USER = launcher.USER
        self.KBDS = launcher.KBDS
        self.session = launcher.session
        self.player = launcher.player
        self.debug = launcher.debug

    def quit(self):
        self.leaving = True

    def cleanup(self):
        pg.display.quit()
