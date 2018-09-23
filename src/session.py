from datetime import time
import src.game_objs as u

import logging
Log = logging.getLogger('MainLogger')

class Session:
    '''Session is a single game run, handles interactions between app,
            board, players etc
        Constructor Parameters:
            app_inst [Application] Application instance
    '''
    def __init__(self, app_inst):
        Log.debug('Starting gamesession instance')
        self.TICKS_PER_SEC = 30
        self.app_inst = app_inst
        self.in_lobby = True
        self.players = []
        self.objects = []
        self.is_paused = True
        self.tick = 0
        self.elapsed = 0

    def begin(self):
        self.is_paused = False

    def update(self):
        #Log.debug('Tick {}'.format(self.tick%100))
        self.tick += 1
        if self.tick % self.TICKS_PER_SEC == 0:
            self.elapsed += 1
        for obj in self.objects:
            obj.update(self.tick)

    def set_board(self, board):
        '''Adds board to session instance'''
        Log.info('Setting session board')
        self.board = board
        self.app_inst.pg_receive_bgr(board.gen_background())
        for point, key in board.objects_toplace:
            if 'norm' in key or 'rich' in key: # Resource
                value = self.app_inst.GAME.rsrc_norm_value
                if 'rich' in key:
                    value = self.app_inst.GAME.rsrc_rich_value
                if   'wood' in key:
                    object = u.WoodField(self, point, value)
                elif 'iron' in key:
                    object = u.IronField(self, point, value)
                elif 'fuel' in key:
                    object = u.FuelField(self, point, value)
                self.add_object(object)

    def add_object(self, object):
        '''Adds map object to session'''
        if object.check_footprint():
            object.apply_footprint()
            self.objects += [object]
            if object.object_type == 'B': object.owner.buildings_count += 1
            if object.object_type == 'U': object.owner.units_count += 1
            self.app_inst.ig_refresh_board = True
            return True
        else:
            return False

    def add_player(self, player):
        '''Add player to game session'''
        Log.info('Adding player {}'.format(player.username))
        self.players += [player]
        player.add_to_session(self)
        coords = self.board.starting_positions[1] # TODO
        self.add_object(u.CommandCenter(self, coords, player))

    def get_color(self, player):
        '''Returns color from color-config'''
        return tuple(self.app_inst.CLRS.player[player.clr_choice])
        # TODO: Let user choose color in lobby-like menu

    def rem_player(self, player):
        '''Remove player from game session'''
        Log.info('Removing player {}'.format(player.username))
        try:
            self.players.remove(player)
            player.leave_session()
            if self.in_lobby:
                self.app_inst.lobby_ui_rem_player(player.name)
        except ValueError: pass # Player not in list

    def toggle_pause(self, force=None):
        Log.info('Toggling pause')
        if force is not None:
            self.is_paused = not self.is_paused
        else:
            self.is_paused = force

    def tell_update_bgr(self):
        '''Triggered by units when moved / destroyed'''
        self.app_inst.ig_refresh_board = True

    def end(self):
        for player in self.players:
            player.leave_session()
