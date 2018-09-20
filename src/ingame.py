import os
import platform
import pygame as pg
from pygame.font import SysFont as Font
import logging
from PIL import Image
Log = logging.getLogger('MainLogger')

class InGame:
    '''Class contains methods related to PyGame'''
    def __init__(self):
        self.pg_init_embed()
        self.pg_load_icons()
        self.pg_load_textures()
        self.embed_size = self.CORE.window_size

    def pg_init_embed(self):
        Log.debug('Initializing embed')
        os.environ['SDL_WINDOWID'] = str(self.pg_embed.winfo_id())
        if platform.system == 'Windows':
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        self.screen = pg.display.set_mode(tuple(self.CORE.window_size))
        pg.font.init()
        pg.display.init()
        pg.display.update()
        # Overlay attributes
        self.cnt_h = 200 # Console central height
        self.sds_h = 320 # Console sides height (and width)

    def pg_update_size(self, evt):
        '''Updates PyGame embed screen size'''
        self.embed_size = evt.width, evt.height
        self.screen = pg.display.set_mode(self.embed_size)
        x, y = self.board_position
        self.screen.blit(self.board_bgr,(0,0),(x,y,*self.embed_size))

    def pg_load_icons(self):
        self.icons = {}
        paths = {
            # Resources
            'wood':     'icons/wood.png',
            'iron':     'icons/iron.png',
            'fuel':     'icons/fuel.png',
            # Attributes
            'heal':     'icons/heal.png',
            'armor':    'icons/armor.png',
            'remain':   'icons/remain.png',
        }
        for key, fn in paths.items():
            pillow = Image.open('img/'+fn)
            self.icons[key] = self.pil_to_surface(pillow)

    def pg_load_textures(self):
        self.textures = {}
        paths = {
            'command':      ('game_obj/commandcenter.png',  True),
            'wall':         ('game_obj/wall.png',           True),
            'tower':        ('game_obj/tower.png',          True),
            'worker':       ('game_obj/worker.png',         True),
            'soldier':      ('game_obj/soldier.png',        True),
            'woodfield':    ('game_obj/woodfield.png',      False),
            'ironfield':    ('game_obj/ironfield.png',      False),
            'fuelfield':    ('game_obj/fuelfield.png',      False),
        }
        for key, (fn, has_plr_clr) in paths.items():
            self.textures[key] = {}
            for sel in [True, False]:
                if not has_plr_clr:
                    pillow = Image.open('img/'+fn)
                    pillow = self.get_colorized(pillow, sel)
                    self.textures[key][sel] = self.pil_to_surface(pillow)
                    continue
                self.textures[key][sel] = {}
                for pkey, plr in self.CLRS.player.items():
                    pillow = Image.open('img/'+fn)
                    pillow = self.get_colorized(pillow, sel, plr)
                    self.textures[key][sel][pkey] = self.pil_to_surface(pillow)

    def pg_receive_bgr(self, bgr):
        self.board_bgr = self.pil_to_surface(bgr)
        x, y = self.board_position
        self.screen.blit(self.board_bgr,(-x,-y))

    def pg_get_texture(self, object):
        texture = self.textures[object.objkey][object.selected]
        if object.object_type in ('B', 'U'):
            texture = texture[object.owner.clr_choice]
        return texture

    def get_colorized(self, texture, selected, own_clr=None):
        toreplace = self.CLRS.txtr_torepl
        select_on = self.CLRS.txtr_slc_on
        select_off =self.CLRS.txtr_slc_off
        width, height = texture.size
        pixels = texture.load()
        pillow = Image.new('RGBA', texture.size)
        newpx = pillow.load()
        for y in range(height):
            for x in range(width):
                color = pixels[x, y]
                if color ==tuple(select_on) and not selected:
                    color = tuple(select_off)
                if color == tuple(toreplace) and own_clr is not None:
                    color = tuple(own_clr)
                newpx[y, x] = color
        return pillow

    @staticmethod
    def pil_to_surface(pil):
        return pg.image.fromstring(pil.tobytes(), pil.size, pil.mode)

    def pg_blit(self):
        mrg = 100 # Margin
        fct = self.CORE.cell_size # Resize factor
        bx, by = self.board_position
        self.screen.blit(self.board_bgr,(-bx,-by))
        objects_list = self.session.objects
        x_rng = bx-mrg, bx+self.embed_size[0]+mrg
        y_rng = by-mrg, by+self.embed_size[1]+mrg
        for object in objects_list:
            x, y = object.coords.get()
            y, x = x*fct, y*fct # NOTE: Reversed coordinates
            if x > x_rng[0] and x < x_rng[1] and y > y_rng[0] and y < y_rng[1]:
                nw = object.footprint.getNW()
                xx, yy = x-nw.x*fct-bx, y-nw.y*fct-by
                texture = self.pg_get_texture(object)
                self.screen.blit(texture, (xx,yy))
        self.pg_blit_console()
        self.pg_blit_resources()

    def pg_blit_console(self):
        emb_w, emb_h = self.embed_size
        rects = [
            pg.Rect((0, emb_h-self.cnt_h),(emb_w, self.cnt_h)),
            pg.Rect((0, emb_h-self.sds_h), (self.sds_h, self.sds_h)),
            pg.Rect((emb_w-self.sds_h,emb_h-self.sds_h),(self.sds_h,self.sds_h))]
        for rect in rects:
            pg.draw.rect(self.screen, pg.Color(*self.CORE.console_clr), rect)
        # Center (skipped when selection is empty)
        if len(self.selection) != 0:
            self.pg_blit_con_selection()

    def pg_blit_con_selection(self):
        font = Font(self.CORE.font_family, self.CORE.fonts['obj_name'][0])
        emb_w, emb_h = self.embed_size
        sp = 5 # Spacing [px]
        if len(self.selection) == 1:
            text = self.TEXT.mapobj[self.selection[0].objkey]
        else:
            text = str(len(self.selection))+self.TEXT.objcount_suff
        text = font.render(text)
        crect = text.get_rect()
        crect.centerx = 0
        self.screen.blit(text, (emb_w//2, emb_h-self.cnt_h))

    def pg_blit_resources(self):
        font = Font(self.CORE.font_family, self.CORE.fonts['resource'][0])
        emb_w, emb_h = self.embed_size
        sp = 5 # Spacing [px]
        icon_h = 30 + sp  # [px]
        icon_w = 30 + sp  # [px]
        text_wood = font.render(str(self.player.rsrc_wood),False,(255,255,255))
        text_iron = font.render(str(self.player.rsrc_iron),False,(255,255,255))
        text_fuel = font.render(str(self.player.rsrc_fuel),False,(255,255,255))
        text_wood.get_rect().right = 0
        text_iron.get_rect().right = 0
        text_fuel.get_rect().right = 0
        self.screen.blit(self.icons['wood'], (emb_w-icon_w, sp))
        self.screen.blit(text_wood, (emb_w-2*icon_w, sp))
        self.screen.blit(self.icons['iron'], (emb_w-icon_w, sp+icon_h))
        self.screen.blit(text_iron, (emb_w-2*icon_w, sp+icon_h))
        self.screen.blit(self.icons['fuel'], (emb_w-icon_w, sp+2*icon_h))
        self.screen.blit(text_fuel, (emb_w-2*icon_w, sp+2*icon_h))


    ################################
    # PyGame events and actions

    def pg_handle(self, evt):
        if evt.type == pg.MOUSEMOTION:
            if evt.buttons[1]: self.pg_board_drag(evt.rel)
        elif evt.type == pg.MOUSEBUTTONDOWN:
            if evt.button == 1: self.pg_board_lclick(evt.pos)

    def pg_board_drag(self, rel):
        rel_x, rel_y = rel
        x, y = self.board_position
        self.board_position = x - rel_x, y - rel_y

    def pg_board_lclick(self, pos):
        fct = self.CORE.cell_size
        x, y = pos
        x, y = x//fct, y//fct
        if self.pg_pointing_target:
            self.pg_set_target(x, y)
        else:
            self.pg_select(x, y)

    def pg_set_target(self):
        self.pg_pointing_target = False
        self.pg_target = x, y

    def pg_select(self, x, y):
        board = self.session.board
        shift = pg.key.get_mods() & pg.KMOD_LSHIFT
        if board.board[y][x].is_occupied:
            object = board.board[y][x].object
            object.select()
            if shift:
                self.selection += [object]
            else:
                for obj in self.selection:
                    obj.deselect()
                self.selection = [object]
        else:
            self.pg_deselect_all()

    def pg_deselect_all(self):
        for obj in self.selection:
            obj.deselect()
        self.selection = []
