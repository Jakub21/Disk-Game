import yaml
import pygame as pg
from datetime import datetime
from src.board import Board
from src.gui import Interface
from src.player import Player
from src.session import Session
import src.system as internal

import logging
Log = logging.getLogger('MainLogger')

class Application(Interface):
    def __init__(self, debug=False):
        self.debug = debug
        self.leaving = False
        self.in_session = False
        Log.info('Creating Application instance')
        self.load_config()
        super().__init__()
        self.set_player() # TEMP: This should be triggered at sign-in
        self.mainloop()

    def mainloop(self):
        usec_elapsed = 0
        frames_count = 0
        prev_sec, prev_usec = 0, 0
        usec_elapsed = 0
        ticks_per_sec = 30
        tick_length = 1/ticks_per_sec*1e6
        ticks = 0
        while not self.leaving:
            time = datetime.now()
            sec = time.second
            usec = time.microsecond
            if usec > prev_usec: usec_elapsed += usec - prev_usec
            else: prev_usec += prev_usec - usec
            for evt in pg.event.get():
                self.pg_handle(evt)
            if self.in_ig_view:
                if sec != prev_sec:
                    _ticks = ticks-ticks_per_sec
                    _ticks = ('{} Behind'.format(abs(_ticks)) if _ticks < 0 \
                    else '{} Ahead'.format(_ticks)) if _ticks != 0 else 'OK'
                    Log.info('FPS: {}   \tTicks: {}'.format(frames_count,_ticks))
                    #Log.debug(self.vars)
                    ticks = 0
                    frames_count = 0
                if usec_elapsed >= tick_length:
                    usec_elapsed -= tick_length
                    self.session.update()
                    ticks += 1
                self.pg_blit_all()
            pg.display.update()
            self.root.update()
            frames_count += 1
            prev_sec, prev_usec = sec, usec

    def load_config(self):
        '''Loads configuration files'''
        Log.debug('Loading config files')
        self.CORE = internal.to_ns(yaml.load(open('cnf/core.yml', 'r')))
        self.TEXT = internal.to_ns(yaml.load(open('cnf/text.yml', 'r')))
        self.CLRS = internal.to_ns(yaml.load(open('cnf/clrs.yml', 'r')))
        self.GAME = internal.to_ns(yaml.load(open('cnf/game.yml', 'r')))

    def set_player(self):
        '''Creates player'''
        self.player = Player(self, 'Local', 'aaa') # TEMP

    def session_start(self, variant):
        '''Starts game session'''
        Log.info('Starting session')
        self.in_session = True
        # Initializing required variables
        self.pg_pointing_target = False
        self.pg_pointing_for = None
        self.selection = []
        # Starting session
        self.session = Session(self)
        path = self.CORE.mapsource_dir + variant + self.CORE.mapsource_suff
        self.session.set_board(Board(self.session, path))
        self.session.add_player(self.player)
        self.session.begin()
        self.ui_show_ig_view() # TEMP

    def session_end(self):
        '''Ends session and performs clean-up'''
        self.session.end()
        del self.session
        del self.screen
        del self.board_bgr
        del self.vars
        del self.ig_refresh_board
        del self.pg_pointing_target
        del self.pg_pointing_for
        del self.selection
        del self.minimap_bgr
        self.in_session = False

    def quit(self):
        '''Application quit method'''
        Log.info('Leaving app')
        self.leaving = True
        if self.in_session:
            self.session_end()
        self.ui_toggle_fullscreen(False)
        self.root.destroy()
