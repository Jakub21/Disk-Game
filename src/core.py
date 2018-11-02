import pygame as pg
from datetime import datetime
from src.handlers import Handlers
from src.interface import Interface
from src.system import to_ns

import logging
Log = logging.getLogger('MainLogger')

class Application(Handlers, Interface):
    def __init__(self, launcher):
        Log.info('Starting game')
        self.leaving = False
        self.back_to_launcher = False
        self.extract_lnch(launcher)
        self.timer_init()
        self.session.reinit(self)
        self.ui_init()
        self.handlers_init()
        self.begin()

    def loop(self):
        if self.timer_update():
            self.session.update()
            if self.timer_changed_sec():
                self.timer_info()
                self.timer_reset()
        for evt in pg.event.get():
            self.evt_handle(evt)
        pg.display.update()
        if not self.session.is_paused:
            self.blit_full()

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

    def begin(self):
        self.session.begin()

    def tell_defeated(self):
        Log.debug('Defeated!')
        self.back_to_launcher = True
        self.leaving = True

    def quit(self):
        self.leaving = True

    def cleanup(self):
        pg.display.quit()

    # Timer methods

    def timer_init(self):
        t = to_ns({})
        t.ticks = 0
        t.frames = 0
        t.ticks_per_sec = self.GAME.ticks_per_sec
        t.tick_len = 1e6/(t.ticks_per_sec) # [us]
        t.prev_sec, t.prev_usec = 0, 0
        t.sec, t.usec = 0, 0
        t.us_elapsed = 0
        self.timer = t

    def timer_update(self):
        t = self.timer
        now = datetime.now()
        t.sec, t.usec = now.second, now.microsecond
        t.frames += 1
        delta_usec = (t.usec - t.prev_usec)%1e6
        t.prev_usec = t.usec
        t.us_elapsed += delta_usec
        if t.us_elapsed >= t.tick_len:
            t.us_elapsed -= t.tick_len
            t.ticks += 1
            return True
        return False

    def timer_changed_sec(self):
        t = self.timer
        return t.prev_sec != t.sec

    def timer_reset(self):
        t = self.timer
        t.ticks = 0
        t.frames = 0
        t.prev_sec = t.sec

    def timer_info(self):
        t = self.timer
        ticks = t.ticks - t.ticks_per_sec
        relative = ('{} behind'.format(abs(ticks)) if ticks < 0 \
            else '{} ahead'.format(ticks)) if ticks != 0 else 'OK'
        Log.info('FPS: {}   \tTicks: {}'.format(t.frames, relative))
