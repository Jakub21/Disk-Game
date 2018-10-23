import src.objects as o

import logging
Log = logging.getLogger('MainLogger')

class Session:
    def __init__(self, launcher):
        self.app = launcher
        self.reinitialized = False
        self.is_paused = True
        self.tick = 0
        self.players = []
        self.objects = []

    def reinit(self, app):
        self.app = app
        self.reinitialized = True
        self.app.tell_board_size(board.size)

    def begin(self):
        self.is_paused = False

    def set_board(self, board):
        Log.debug('Adding board to session')
        self.board = board
        for point, key in board.toplace:
            if 'norm' in key or 'rich' in key: # Resource
                value = self.app.GAME.rsrc_rich_value if 'rich' in key \
                    else self.app.GAME.rsrc_norm_value
                if   'wood' in key:
                    object = o.WoodField(self, point, value)
                elif 'iron' in key:
                    object = o.IronField(self, point, value)
                elif 'fuel' in key:
                    object = o.FuelField(self, point, value)
            r = self.add_object(object)

    def add_object(self, object):
        if not self.board.apply_fp(object):
            return False
        self.objects += [object]
        if object.otype == 'B': object.owner.blnd_count += 1
        if object.otype == 'U': object.owner.unit_count += 1
        if self.reinitialized: self.tell_tell_dirty()
        return True

    def add_player(self, player):
        Log.info('Adding player {}'.format(player.username))
        self.players += [player]
        player.add_to_session(self)
        cc_coords = self.board.starts[len(self.players)-1]
        player.home_cc_pos = cc_coords
        self.add_object(o.CommandCenter(self, cc_coords, player))

    def rem_player(self, player):
        Log.info('Removing player {}'.format(player.username))
        try:
            self.players.remove(player)
            player.leave_session()
        except ValueError: pass

    def get_color(self, player):
        return tuple(self.app.CLRS.player[player.clr_choice])

    def tell_tell_dirty(self):
        self.app.tell_dirty()

    def toggle_pause(self, force=None):
        Log.info('Toggling pause')
        if force is not None:
            self.is_paused = not self.is_paused
        else:
            self.is_paused = force
