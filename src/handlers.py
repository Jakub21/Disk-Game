import pygame as pg
from src.system import to_ns
from src.geometry import Point

import logging
Log = logging.getLogger('MainLogger')

class Handlers:
    '''Method-container class. Contains event-handling-related methods'''

    def handlers_init(self):
        self.pointing_onboard = False
        self.pointing_for = None
        self.selection = []
        self.make_regions()

    def make_regions(self):
        v = self.ui_vars
        self.regions = to_ns({})
        self.regions.board = pg.Rect(0, 0, v.disp_w, v.disp_h-v.cns_ss)
        self.regions.notch = pg.Rect(v.cns_ss, v.disp_h-v.cns_ss,
            v.disp_w-2*v.cns_ss, v.cns_ss-v.cns_ch)

    def evt_handle(self, evt):
        r = self.regions
        if evt.type == pg.QUIT:
            self.quit()
        if evt.type == pg.MOUSEMOTION:
            if r.board.collidepoint(evt.pos) or r.notch.collidepoint(evt.pos):
                if evt.buttons[1]: self.evt_board_drag(evt.rel)
        if evt.type == pg.MOUSEBUTTONDOWN:
            if r.board.collidepoint(evt.pos) or r.notch.collidepoint(evt.pos):
                if evt.button == 1: self.evt_board_lclick(evt.pos)
            if r.board.collidepoint(evt.pos) or r.notch.collidepoint(evt.pos):
                if evt.button == 3: self.evt_board_rclick(evt.pos)

    def evt_board_drag(self, rel):
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
        v = self.ui_vars
        x, y = pos
        x, y = round(x/v.cell_px,3)+v.b_sx, round(y/v.cell_px,3)+v.b_sy
        if self.pointing_onboard:
            self.evt_point_target((x,y))
        else:
            self.evt_select((x,y))

    def evt_point_target(self, pos):
        pass

    def evt_select(self, pos):
        v = self.ui_vars
        board = self.session.board
        shift = pg.key.get_mods() & pg.KMOD_SHIFT
        x, y = pos
        object = board.get_object((x,y))
        if object is not None:
            if shift:
                if object.selected:
                    object.deselect()
                    self.selection.remove(object)
                else:
                    object.select()
                    self.selection += [object]
            else:
                self.deselect_all()
                object.select()
                self.selection = [object]
        else:
            if not shift: self.deselect_all()
            # Clicking with shift at an empty cell does nothing
        self.sort_selection()
        self.tell_dirty()

    def evt_board_rclick(self, pos):
        v = self.ui_vars
        x, y = pos
        x, y = round(x/v.cell_px,3)+v.b_sx, round(y/v.cell_px,3)+v.b_sy
        self.temp_place_worker((x,y))

    def temp_place_worker(self, pos):
        import src.objects as o
        v = self.ui_vars
        board = self.session.board
        worker = o.Worker(board, Point(*pos), self.player)
        if not self.session.add_object(worker):
            del worker


    def update_board_pos(self):
        v = self.ui_vars
        v.b_sx = v.v_sx // v.cell_px
        v.b_sy = v.v_sy // v.cell_px

    # Selection-related methods

    def deselect_all(self):
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
            Log.warn('oTypes {} are not assigned to selection order'.format(l))
