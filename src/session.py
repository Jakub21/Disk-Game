import src.objects as o
from src.cmd_defines import AllCommands

import logging
Log = logging.getLogger('MainLogger')

class Session:
    def __init__(self, launcher):
        Log.debug('Starting session')
        self.app = launcher
        self.reinitialized = False
        self.is_paused = True
        self.tick = 0
        self.players = []
        self.objects = []
        self.ticks_per_sec = self.app.GAME.ticks_per_sec
        self.cmds = AllCommands()

    def reinit(self, app):
        self.app = app
        self.reinitialized = True

    def begin(self):
        self.is_paused = False

    def update(self):
        self.tick += 1
        for obj in self.objects:
            obj.update(self.tick)

    def set_board(self, board):
        Log.debug('Adding board to session')
        self.board = board
        for point, key in board.toplace:
            if 'norm' in key or 'rich' in key: # Resource
                value = self.app.GAME.rsrc_rich_value if 'rich' in key \
                    else self.app.GAME.rsrc_norm_value
                if   'wood' in key:
                    obj = o.WoodField(self, point, value)
                elif 'iron' in key:
                    obj = o.IronField(self, point, value)
                elif 'fuel' in key:
                    obj = o.FuelField(self, point, value)
            r = self.add_object(obj)

    def add_object(self, obj):
        self.objects += [obj]
        if obj.otype == 'B': obj.owner.blnd_count += 1
        if obj.otype == 'U': obj.owner.unit_count += 1
        if not self.board.apply_fp(obj):
            self.rem_object(obj)
            return False
        if self.reinitialized: self.tell_tell_dirty()
        return True

    def rem_object(self, obj):
        try:
            player = obj.owner
            if obj.otype == 'B': player.blnd_count -= 1
            elif obj.otype == 'U': player.unit_count -= 1
            if player.blnd_count == 0:
                player.defeat()
                if self.app.player is player:
                    self.app.tell_defeated()
        except AttributeError:
            pass
        self.tell_tell_dirty()
        self.board.release_fp(obj)
        try: self.app.selection.remove(obj)
        except ValueError: pass
        try: self.objects.remove(obj)
        except ValueError: pass
        del obj

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

    def tell_destroyed(self, obj):
        self.rem_object(obj)

    def request_subpercell(self):
        return self.app.CORE.sub_per_cell

    def tell_required(self, player, what):
        '''Tells player what is required, triggered by Command.do_instant'''
        Log.debug('Player {} needs more {}'.format(player.username, what))
        # TODO
