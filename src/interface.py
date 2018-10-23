import pygame as pg
from os import listdir
from PIL import Image
from math import ceil
from pygame.font import SysFont as Font
from src.system import to_ns

import logging
Log = logging.getLogger('MainLogger')

class Interface:
    '''Method-container class. Contains interface-related methods'''

    def ui_init(self):
        Log.debug('Initializing UI')
        self.screen = pg.display.set_mode((0,0),pg.FULLSCREEN|pg.HWSURFACE)
        self.refresh_terrain = True
        pg.font.init()
        pg.display.init()
        self.make_colors()
        self.make_ui_vars()
        self.blit_loading()
        self.load_gfx(self.session.board.variant)

    def tell_dirty(self):
        self.refresh_terrain = True

    def make_colors(self):
        self.colors = to_ns({})
        self.colors.white = pg.Color(255,255,255)
        self.colors.gdark = pg.Color( 46, 46, 46) # Standard dark gray
        self.colors.vdark = pg.Color( 35, 35, 35)
        self.colors.black = pg.Color(  0,  0,  0)

    def make_ui_vars(self):
        self.ui_vars = to_ns({})
        v = self.ui_vars
        disp = pg.display.Info()
        brd = self.session.board
        home = self.player.home_cc_pos
        c = self.CORE
        # Constants
        v.subc_px = c.pix_per_sub                   #SubCell:Size
        v.cell_px = v.subc_px*c.sub_per_cell        #Cell:Size
        # Interface (Constants)
        v.cns_ch = 200                              #Console:Center:Size:Y
        v.cns_ss = 320                              #Console:Sides:Size
        v.ccap_crty = -28                           #Console:Cap:Correction:Y
        v.ccap_crtx = -48                           #Console:Cap:R:Correction:X
        v.csel_th = 32                              #Console:Selection:Text:Y
        v.csel_cols = 8                             #Console:Selection:Columns
        v.csel_rows = 3                             #Console:Selection:Rows
        v.csel_spc = 8                              #Console:Selection:Spacing
        v.cicos = 40                                #Console:Icons:Size
        v.cspc = 2                                  #Console:Spacing
        # Session- or Device- specific
        v.disp_w = disp.current_w                   #Display:Size:X
        v.disp_h = disp.current_h                   #Display:Size:Y
        v.disp_cx = v.disp_w//2                     #Display:Center:X
        v.disp_cy = v.disp_h//2                     #Display:Center:Y
        v.db_w = disp.current_w                     #Display:Board:Size:X
        v.db_h = disp.current_h-v.cns_ch            #Display:Board:Size:Y
        v.db_cx = v.db_w//2                         #Display:Board:Center:X
        v.db_cy = v.db_h//2                         #Display:Board:Center:Y
        v.brd_w = brd.size[0]*v.cell_px             #Board:Size:X[px]
        v.brd_h = brd.size[1]*v.cell_px             #Board:Size:Y[px]
        # Current view
        v.v_sx = home.x*v.cell_px-v.db_cx           #View:Shift:X
        v.v_sy = home.y*v.cell_px-v.db_cy           #View:Shift:Y
        v.bidx = ceil(v.db_w/v.cell_px)             #View:CellsInDisplay:X
        v.bidy = ceil(v.db_h/v.cell_px)             #View:CellsInDisplay:Y
        v.b_sx = v.v_sx//v.cell_px                  #Board:Shift:X
        v.b_sy = v.v_sy//v.cell_px                  #Board:Shift:Y
        # Interface (Calculated)
        v.csel_ofx = v.disp_w//2 -2*v.cicos         #Console:Selection:Offxet:X
        v.csel_ofy = v.csel_th+v.disp_h-v.cns_ch    #Console:Selection:Offset:Y

    def load_gfx(self, vr):
        '''Loads graphics (vr parameter is terrain textures variant)'''
        v = self.ui_vars
        self.gfx = to_ns({})
        self.gfx.terrain = self.get_all_gfx('img/terrain/{}/'.format(vr), '.png')
        self.gfx.ui = self.get_all_gfx('img/ui/', '.png')
        self.gfx.icons = self.get_all_gfx('img/icons/', '.png')
        self.gfx.objs = self.get_all_gfx('img/objects/', '.png', pil=True)
        for key, image in self.gfx.objs.items():
            Log.debug('Creating color variants of {} texture'.format(key))
            self.gfx.objs[key] = self.make_clr_variants(image)
        self.gfx.grayed = self.get_all_gfx('img/objects/', '.png', pil=True)
        for key, image in self.gfx.grayed.items():
            gray = image.convert('L')
            gray = gray.resize((v.cicos,v.cicos))
            self.gfx.grayed[key] = self.pil_to_srf(gray.convert('RGB'))

    def blit_loading(self):
        clrs = self.colors
        v = self.ui_vars
        font = Font(self.CORE.font_family, self.CORE.fonts['loading'][0])
        text = font.render(self.TEXT.loading, False, clrs.white)
        rect = text.get_rect()
        rect.centerx = v.disp_cx
        rect.centery = v.disp_cy
        self.screen.fill(clrs.gdark)
        self.screen.blit(text, rect)

    def blit_full(self):
        self.blit_terrain()
        self.blit_objects()
        self.blit_console()

    def blit_terrain(self):
        if not self.refresh_terrain:
            return
        self.refresh_terrain = False
        v = self.ui_vars
        board = self.session.board
        for y in range(v.bidy):
            for x in range(v.bidx):
                cell = board.get((x+v.b_sx,y+v.b_sy))
                texture = self.gfx.terrain['taken'] if cell.occupied == 2 else \
                    self.gfx.terrain[cell.variant]
                xx, yy = x*v.cell_px, y*v.cell_px
                self.screen.blit(texture, (xx,yy))

    def blit_objects(self):
        v = self.ui_vars
        objects = self.session.objects
        for object in objects:
            if not self.check_obj_onscreen(object): continue
            try: texture = self.gfx.objs[object.objkey][object.owner.clr_choice]
            except AttributeError: texture = self.gfx.objs[object.objkey]['red']
            size = object.footprint.size
            xmod, ymod = 0, 0
            if object.footprint.is_square: size = (size-1)//2
            else: xmod, ymod = 0.5*size, 0.5*size
            x = (object.coords.x - v.b_sx - size + xmod)*v.cell_px
            y = (object.coords.y - v.b_sy - size + ymod)*v.cell_px
            self.screen.blit(texture, (x, y))

    def blit_console(self):
        v = self.ui_vars
        self.screen.fill(self.colors.vdark,
            (0, v.disp_h-v.cns_ss, v.cns_ss, v.cns_ss))
        self.screen.fill(self.colors.vdark,
            (v.disp_w-v.cns_ss, v.disp_h-v.cns_ss, v.cns_ss, v.cns_ss))
        self.screen.fill(self.colors.vdark,
            (v.cns_ss, v.disp_h-v.cns_ch, v.disp_w-2*v.cns_ss, v.cns_ch))
        self.screen.blit(self.gfx.ui['console_cap_l'],
            (0, v.disp_h-v.cns_ss+v.ccap_crty))
        self.screen.blit(self.gfx.ui['console_cap_r'],
            (v.disp_w+v.ccap_crtx-v.cns_ss, v.disp_h-v.cns_ss+v.ccap_crty))
        self.blit_cns_selection()

    def blit_cns_selection(self):
        v = self.ui_vars
        font = Font(self.CORE.font_family, self.CORE.fonts['obj_name'][0])
        of_x, of_y = v.csel_ofx, v.csel_ofy
        cntr_w = v.disp_w - 2*v.cns_ss
        text = ''
        # Selection attrs / list
        if len(self.selection) == 1:
            text = self.TEXT.objects[self.selection[0].objkey]
            if self.debug:
                text += self.selection[0].get_address()
            index = 0
            for key, value in self.selection[0].get_attrs().items():
                icon = self.gfx.icons[key]
                vtext = font.render(str(value), False, self.colors.white)
                y = of_y + index*(v.cicos+v.cspc)
                self.screen.blit(icon, (of_x, y))
                self.screen.blit(vtext,  (of_x+v.cicos+v.cspc, y))
                index += 1
        elif len(self.selection) > 1:
            text = str(len(self.selection))+self.TEXT.obj_count_suffix
            sect_w = v.csel_cols*(v.cicos+v.csel_spc)-v.csel_spc
            i = 0
            for object in self.selection:
                texture = self.gfx.grayed[object.objkey]
                x = (i% v.csel_cols) * (v.cicos+v.csel_spc)
                y = (i//v.csel_cols) * (v.cicos+v.csel_spc)
                x = x + cntr_w//2 + v.cns_ss - sect_w//2
                y = y + v.disp_h - v.cns_ch + 2*v.csel_spc + v.csel_th
                self.screen.blit(texture, (x,y))
                i += 1
                if i > v.csel_cols * v.csel_rows:
                    break
        # Selection main text
        text = font.render(text, False, self.colors.white)
        crect = text.get_rect()
        crect.top = v.disp_h - v.cns_ch
        crect.centerx = cntr_w//2 + v.cns_ss
        self.screen.blit(text, crect)

    # Helper methods

    def check_obj_onscreen(self, object):
        v = self.ui_vars
        fp = object.footprint
        m = fp.size
        if object.coords.x+m > v.b_sx and object.coords.x-m < v.b_sx+v.db_w:
            if object.coords.y+m > v.b_sy and object.coords.y-m < v.b_sy+v.db_h:
                return True
        return False

    def make_clr_variants(self, image):
        colors = self.CLRS.player
        toreplace = tuple(self.CLRS.txtr_player_clr)
        source_px = image.load()
        w, h = image.size
        results = {}
        for key, color in colors.items():
            result = image.copy()
            result_px = result.load()
            color = tuple(color)
            for y in range(h):
                for x in range(w):
                    if source_px[y, x] == toreplace:
                        result_px[y, x] = color
            results[key] = self.pil_to_srf(result)
        return results


    def get_all_gfx(self, path, suffix, pil=False):
        result = {}
        for filename in listdir(path):
            if not filename.endswith(suffix):
                continue
            image = Image.open(path+filename)
            if not pil:
                image = self.pil_to_srf(image)
            key = filename.replace(suffix, '')
            result[key] = image
        return result

    @staticmethod
    def pil_to_srf(pillow):
        return pg.image.fromstring(pillow.tobytes(), pillow.size, pillow.mode)
