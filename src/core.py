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
    def __init__(self):
        self.leaving = False
        Log.info('Creating Application instance')
        self.load_config()
        super().__init__()
        self.set_player() # TEMP: This should be triggered at sign-in
        self.mainloop()

    def mainloop(self):
        prev_s, count = 0, 0
        while not self.leaving:
            s = datetime.now().second
            count += 1
            if s != prev_s:
                if self.in_ig_view:
                    Log.info('FPS: {}'.format(count))
                    Log.debug(len(self.selection))
                count = 0
            prev_s = s
            for evt in pg.event.get():
                self.pg_handle(evt)
            if self.in_ig_view:
                self.pg_blit()
            pg.display.update()
            self.root.update()

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
        self.board_position = 0, 0
        self.embed_size = self.CORE.window_size
        self.selection = []
        self.pg_target = 0, 0
        # Starting session
        self.session = Session(self)
        path = self.CORE.mapsource_dir + variant + self.CORE.mapsource_suff
        self.session.set_board(Board(self.session, path))
        self.session.add_player(self.player)
        self.ui_show_ig_view() # TEMP


    def session_end(self):
        '''Ends session and performs clean-up'''
        self.session.end()
        del self.session
        del self.screen
        del self.embed_size
        del self.board_bgr
        del self.board_position
        del self.pg_pointing_target
        del self.pg_target
        del self.selection
        self.in_session = False

    def quit(self):
        '''Application quit method'''
        Log.info('Leaving app')
        self.leaving = True
        if self.in_session:
            self.session_end()
        self.ui_toggle_fullscreen(False)
        self.root.destroy()
