from PIL.ImageColor import getrgb as get_rgb_core

import logging
Log = logging.getLogger('MainLogger')

class Player:
    def __init__(self, app_inst, username, password):
        self.app_inst = app_inst
        self.username = username
        self.clr_choice = 'yellow' # TODO
        self.validate_login(password)
        del password

    def validate_login(self, password):
        self.valid = True
        if len(self.username) == 0:
            self.valid = 'no_username'
            return
        if len(password) == 0:
            self.valid = 'no_password'
            return

    def add_to_session(self, session):
        '''Inits attributes required to join session'''
        self.color = session.get_color(self)
        self.session = session
        self.buildings_count = 0
        self.units_count = 0
        self.rsrc_wood = 500
        self.rsrc_iron = 50
        self.rsrc_fuel = 0

    def leave_session(self):
        '''Clean-up performed at session exit'''
        Log.debug('Clean-up at leave')
        del self.session
        del self.buildings_count
        del self.units_count
        del self.rsrc_wood
        del self.rsrc_iron
        del self.rsrc_fuel

    def defeat(self):
        '''Triggered when player has no buildings left'''
        Log.info('Player defeated')
        self.leave_session()

    def tell_destroyed(self, object):
        '''Triggered by player-owned units when destroyed'''
        if object.object_type == 'B': self.buildings_count -= 1
        if object.object_type == 'U': self.units_count -=1
        if self.buildings_count == 0:
            self.defeat()
        self.app_inst.ig_refresh_board = True

    def pay(self, rsrc):
        '''Subtracts given amount from account. Parameter is 3-tuple of ints'''
        wood, iron, fuel = rsrc
        if wood > self.rsrc_wood:
            Log.info('Not enough wood')
            return 'no_wood'
        if iron > self.rsrc_iron:
            Log.info('Not enough iron')
            return 'no_iron'
        if fuel > self.rsrc_fuel:
            Log.info('Not enough fuel')
            return 'no_fuel'
        self.rsrc_wood -= wood
        self.rsrc_iron -= iron
        self.rsrc_fuel -= fuel
        return True

    def giveback(self, rsrc):
        '''Give back some amount of resources. Use when something is canceled'''
        wood, iron, fuel = rsrc
        self.rsrc_wood += wood
        self.rsrc_iron += iron
        self.rsrc_fuel += fuel
