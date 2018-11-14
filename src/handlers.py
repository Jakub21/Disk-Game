import pygame as pg
from src.system import to_ns
from src.geometry import Point

import logging
Log = logging.getLogger('MainLogger')

class Handlers:
    '''Method-container class. Contains event-handling-related methods'''

    def handlers_init(self):
        self.pointing = False
        self.pointing_for = (None, None)
        self.selection = []
        self.make_regions()

    def make_regions(self):
        '''Creates screen regions'''
        v = self.ui_vars
        self.regions = to_ns({})
        self.regions.board = pg.Rect(0, 0, v.disp_w, v.disp_h-v.cns_ss)
        self.regions.notch = pg.Rect(v.cns_ss, v.disp_h-v.cns_ss,
            v.disp_w-2*v.cns_ss, v.cns_ss-v.cns_ch)
        self.regions.cmnds = pg.Rect(v.ccmd_ofx, v.ccmd_ofy,
            v.ccmd_cols*(v.cicos+v.cspc), v.ccmd_rows*(v.cicos+v.cspc))

    def evt_handle(self, evt):
        '''Receives event and starts related methods'''
        r = self.regions
        if evt.type == pg.QUIT:
            self.quit()
        if evt.type == pg.MOUSEMOTION:
            if r.board.collidepoint(evt.pos) or r.notch.collidepoint(evt.pos):
                if evt.buttons[1]: self.evt_board_drag(evt.rel)
        if evt.type == pg.MOUSEBUTTONDOWN:
            if r.board.collidepoint(evt.pos) or r.notch.collidepoint(evt.pos):
                if evt.button == 1: self.evt_board_lclick(evt.pos)
                if evt.button == 3: self.evt_board_rclick(evt.pos)
            elif r.cmnds.collidepoint(evt.pos):
                if evt.button == 1: self.evt_cmnd_lclick(evt.pos)

    def evt_board_drag(self, rel):
        '''mouse movement over board with CMB pressed'''
        v = self.ui_vars
        rel_x, rel_y = rel
        if self.USER.reversed_drag:
            x, y = v.v_sx + rel_x, v.v_sy + rel_y
        else:
            x, y = v.v_sx - rel_x, v.v_sy - rel_y
        if x < 0: x = 0
        if x > v.brd_w - v.db_w: x = v.brd_w - v.db_w
        if y < 0: y = 0
        if y > v.brd_h - v.db_h: y = v.brd_h - v.db_h
        v.v_sx, v.v_sy = x, y
        self.update_board_pos()
        self.tell_dirty()

    def evt_board_lclick(self, pos):
        '''LMB click on board'''
        v = self.ui_vars
        x, y = pos
        x, y = round(x/v.cell_px,3)+v.b_sx, round(y/v.cell_px,3)+v.b_sy
        if self.pointing:
            self.act_point((x,y))
        else:
            self.act_select((x,y))

    def evt_board_rclick(self, pos):
        '''RMB click on board'''
        v = self.ui_vars
        x, y = pos
        x, y = round(x/v.cell_px,3)+v.b_sx, round(y/v.cell_px,3)+v.b_sy

    def evt_cmnd_lclick(self, pos):
        '''LMB click on commands panel'''
        if self.selection == []:
            return
        if self.selection[0].owner is not self.player:
            return
        v = self.ui_vars
        x, y = pos
        x, y = x - v.ccmd_ofx, y - v.ccmd_ofy
        icowsp = v.cicos + v.cspc # Icon with spacing
        if x%icowsp >= v.cicos or y%icowsp >= v.cicos:
            return # Spacing, not icon
        x, y = x//icowsp, y//icowsp
        key, command = self.selection[0].get_cmd((x,y))
        if key == None:
            return # Empty slot
        self.act_execute_cmnd(self.selection, command)

    def update_board_pos(self):
        v = self.ui_vars
        v.b_sx = v.v_sx // v.cell_px
        v.b_sy = v.v_sy // v.cell_px

    # Actions

    def act_select(self, pos):
        v = self.ui_vars
        board = self.session.board
        shift = pg.key.get_mods() & pg.KMOD_SHIFT
        x, y = pos
        obj = board.get_object((x,y))
        if obj is not None:
            if shift:
                if obj.selected:
                    obj.deselect()
                    self.selection.remove(obj)
                else:
                    obj.select()
                    self.selection += [obj]
            else:
                self.act_deselect_all()
                obj.select()
                self.selection = [obj]
        else:
            if not shift: self.act_deselect_all()
            # Clicking with shift at an empty cell does nothing
        self.sort_selection()
        self.tell_dirty()

    # Command execution-related methods

    def act_execute_cmnd(self, scope, command):
        if command.takes_pt or command.takes_obj:
            self.pointing_for = (command, scope)
            self.pointing = True
        else:
            command.start(self.session, scope)

    def act_point(self, coords):
        command, scope = self.pointing_for
        if command.takes_pt:
            self.act_point_coords(coords)
        else:
            self.act_point_object(coords)

    def act_point_coords(self, coords):
        command, scope = self.pointing_for
        command.start(self.session, scope, coords)
        self.pointing_for = (None, None)
        self.pointing = False

    def act_point_object(self, coords):
        command, scope = self.pointing_for
        obj = self.session.board.get_object(coords)
        command.start(self.session, scope, obj)
        self.pointing_for = (None, None)
        self.pointing = False

    # Selection-related methods

    def act_deselect_all(self):
        for obj in self.selection:
            obj.deselect()
        self.selection = []

    def sort_selection(self):
        old_len = len(self.selection)
        old_sel = [o for o in self.selection]
        sorted = []
        types_order = self.GAME.types_order
        for obj_type in types_order:
            for obj in self.selection:
                if obj.objkey == obj_type: sorted += [obj]
        self.selection = sorted
        if old_len != len(self.selection):
            l = [o.objkey for o in old_sel if o not in self.selection]
            Log.warn('Objects {} are not assigned to selection order'.format(l))
