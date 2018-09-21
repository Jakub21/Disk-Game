import os
import platform
import pygame as pg
from pygame.font import SysFont as Font
import logging
from PIL import Image
Log = logging.getLogger('MainLogger')

class InGameVars:
    '''Contains in-game UI variables and constants'''
    def __init__(self, a):
        self.emb_w,self.emb_h = 0,0 # Embed:Size
        self.brx, self.bry = 0, 0   # Board:Offset
        self.brw, self.brh = 0, 0   # Board:Size
        self.mrg = 100              # Board:BlitMargin
        self.fct = a.CORE.cell_size # Board:ResizeFactor
        self.cch = 200              # Console:CenterHeight
        self.csh = 320              # Console:SidesHeight
        self.cs_ofs = 30            # Console:Selection:Offset_Ver
        self.cicon = 40             # Console:Selection:IconSize
        self.cs_sp = 2              # Console:Selection:Spacing
        self.mmh = 270              # Console:Minimap:Size
        self.mmx, self.mmy = 0, 0   # Console:Minimap:Offset
        self.mm_vbw,self.mm_vbh=0,0 # Console:Minimap:ViewBox:Size
        self.mm_vbx,self.mm_vby=0,0 # Console:Minimap:ViewBox:Offset
        self.ct_x,self.ct_y=25,-18  # Console:Counter:Offset
        self.ccap_x = -48           # Console:Texture:Correction_Hor
        self.ccap_y = -28           # Console:Texture:Correction_Ver
        self.ricon = 30             # Resources:IconSize
        self.rs_sp = 5              # Resources:Spacing
        self.white = pg.Color(255,255,255)
        self.black = pg.Color(0,0,0)
        # Board:BlitMargin - How far away center of object can be from
        # screen boundaries and still be included in blitting

    def __repr__(self):
        t = 'InGameVars attributes:\n'
        for key, val in self.__dict__.items():
            t += '\t{}:\t{}\n'.format(key, val)
        return t


class InGame:
    '''Class contains methods related to PyGame'''
    def __init__(self):
        self.pg_init_embed()
        self.pg_load_ui_gfx()
        self.pg_load_icons()
        self.pg_load_textures()
        self.ig_refresh_board = False

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
        self.vars = InGameVars(self)

    def pg_update_size(self, evt):
        '''Updates PyGame embed screen size'''
        v = self.vars
        v.emb_w, v.emb_h = evt.width, evt.height
        self.screen = pg.display.set_mode((v.emb_w, v.emb_h))
        self.ig_refresh_board = True

    def pg_load_ui_gfx(self):
        self.ui_gfx = {}
        paths = {
            'cns_cap_l':    'ui/console_cap_l.png',
            'cns_cap_r':    'ui/console_cap_r.png',
        }
        for key, fn in paths.items():
            pillow = Image.open('img/'+fn)
            self.ui_gfx[key] = self.pil_to_surface(pillow)

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
        round_mask_path = 'img/mask68.png'
        round_mask = Image.open(round_mask_path)
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
            if 'field' in key: # Round white mask as "selected" texture
                pillow = Image.open('img/'+fn)
                self.textures[key][False] = self.pil_to_surface(pillow)
                pillow.paste(round_mask, mask=round_mask)
                self.textures[key][True] = self.pil_to_surface(pillow)
                continue
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
        self.vars.brw, self.vars.brh = bgr.size

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
        v = self.vars
        if self.ig_refresh_board:
            self.screen.blit(self.board_bgr, (0,0),
                (v.brx, v.bry, v.emb_w, v.emb_h-v.cch))
            self.ig_refresh_board = False
        objects_list = self.session.objects
        x_rng = v.brx-v.mrg, v.brx+v.emb_w+v.mrg
        y_rng = v.bry-v.mrg, v.bry+v.emb_h+v.mrg
        for object in objects_list:
            x, y = object.coords.get()
            y, x = x*v.fct, y*v.fct # NOTE: Reversed coordinates
            if x > x_rng[0] and x < x_rng[1] and y > y_rng[0] and y < y_rng[1]:
                nw = object.footprint.getNW()
                xx, yy = x-nw.x*v.fct-v.brx, y-nw.y*v.fct-v.bry
                texture = self.pg_get_texture(object)
                self.screen.blit(texture, (xx,yy))
        self.pg_blit_resources()
        self.pg_blit_console()
        self.pg_blit_minimap()
        self.pg_blit_counter()

    def pg_blit_console(self):
        v = self.vars
        # Console background
        rects = [
            pg.Rect((0, v.emb_h-v.cch),(v.emb_w, v.cch)),
            pg.Rect((0, v.emb_h-v.csh), (v.csh, v.csh)),
            pg.Rect((v.emb_w-v.csh,v.emb_h-v.csh),(v.csh,v.csh))]
        for rect in rects:
            pg.draw.rect(self.screen, pg.Color(*self.CORE.console_clr), rect)
        # Center (skipped when selection is empty)
        if len(self.selection) != 0:
            self.pg_blit_cns_selection()
        # Console Caps (these constants only work with currently used textures)
        x = v.emb_w -v.csh +v.ccap_x
        self.screen.blit(self.ui_gfx['cns_cap_l'], (0, v.emb_h-v.csh+v.ccap_y))
        self.screen.blit(self.ui_gfx['cns_cap_r'], (x, v.emb_h-v.csh+v.ccap_y))

    def pg_blit_cns_selection(self):
        v = self.vars
        font = Font(self.CORE.font_family, self.CORE.fonts['obj_name'][0])
        nn, ww = v.emb_h -v.cch + v.cs_ofs, v.emb_w//2 - 2*v.cicon
        if len(self.selection) == 1:
            text = self.TEXT.mapobj[self.selection[0].objkey]
            index = 0
            for key, value in self.selection[0].get_attrs().items():
                icon = self.icons[key]
                vtext = font.render(str(value),False,v.white)
                n = nn + index*(v.cicon+v.cs_sp)
                self.screen.blit(icon, (ww, n))
                self.screen.blit(vtext, (ww +v.cicon +v.cs_sp, n))
                index += 1
        else:
            text = str(len(self.selection))+self.TEXT.objcount_suff
            pass # TODO
        text = font.render(text, False, v.white)
        crect = text.get_rect()
        crect.top = v.emb_h-v.cch
        crect.centerx = v.emb_w//2
        self.screen.blit(text, crect)

    def pg_blit_resources(self):
        v = self.vars
        font = Font(self.CORE.font_family, self.CORE.fonts['resource'][0])
        icon_h = v.ricon + v.rs_sp
        icon_w = v.ricon + v.rs_sp
        text_wood = font.render(str(self.player.rsrc_wood),False,v.white)
        text_iron = font.render(str(self.player.rsrc_iron),False,v.white)
        text_fuel = font.render(str(self.player.rsrc_fuel),False,v.white)
        wood_rect = text_wood.get_rect()
        iron_rect = text_iron.get_rect()
        fuel_rect = text_fuel.get_rect()
        for i, rect in enumerate([wood_rect, iron_rect, fuel_rect]):
            rect.top = i*icon_h +2*v.rs_sp
            rect.right = v.emb_w -icon_w -v.rs_sp
        self.screen.blit(self.icons['wood'], (v.emb_w-icon_w, v.rs_sp))
        self.screen.blit(text_wood, wood_rect)
        self.screen.blit(self.icons['iron'], (v.emb_w-icon_w, v.rs_sp+icon_h))
        self.screen.blit(text_iron, iron_rect)
        self.screen.blit(self.icons['fuel'], (v.emb_w-icon_w, v.rs_sp+2*icon_h))
        self.screen.blit(text_fuel, fuel_rect)

    def pg_blit_minimap(self):
        v = self.vars
        # Calculations
        csp = (v.csh-v.mmh)//2 # Console Spacing
        v.mmx, v.mmy = csp, v.emb_h-v.csh+csp
        scale_x, scale_y = v.mmh/v.brw, v.mmh/v.brh # map_w = map_h
        scale = min(scale_x, scale_y)
        # Scaling
        v.mm_vbw, v.mm_vbh = int(scale*v.emb_w), int(scale*v.emb_h)
        v.mm_vbx, v.mm_vby = int(scale*v.brx), int(scale*v.bry)
        # Background
        bgr = pg.Rect((v.mmx, v.mmy),(v.mmh, v.mmh))
        pg.draw.rect(self.screen, v.black, bgr)
        # Boundaries of current view
        view = pg.Rect((v.mmx+v.mm_vbx, v.mmy+v.mm_vby), (v.mm_vbw, v.mm_vbh))
        pg.draw.rect(self.screen, v.white, view, 1)

    def pg_blit_counter(self):
        v = self.vars
        font = Font(self.CORE.font_family, self.CORE.fonts['counter'][0])
        x = v.ct_x
        y = v.emb_h - v.csh + v.ct_y
        elapsed = self.session.elapsed
        s = '0'+str(elapsed % 60) if elapsed% 60 < 10 else str(elapsed % 60)
        m = '0'+str(elapsed //60) if elapsed//60 < 10 else str(elapsed //60)
        text = '{}:{}'.format(m, s)
        if elapsed >= 60*60: # 1 hour
            text = '{}:'.format(elapsed//(60*60))+text
        text = font.render(text, False, v.white)
        self.screen.blit(text, (x,y))


    ################################
    # PyGame events and actions

    def pg_handle(self, evt):
        v = self.vars
        # Calculate regions
        notch_n = v.emb_h -v.csh
        notch_h = v.csh -v.cch
        csp = (v.csh-v.mmh)//2 # Console-minimap spacing
        rgn_board = pg.Rect((0, 0), (v.emb_w, v.emb_h-v.csh))
        rgn_notch = pg.Rect((v.csh, notch_n), (v.emb_w-2*v.csh, notch_h))
        rgn_mnmap = pg.Rect((v.mmx, v.mmy),(v.mmh, v.mmh))
        # Check event type and handle it
        if evt.type == pg.MOUSEMOTION:
            pos = evt.pos
            if evt.buttons[1]:
                if rgn_board.collidepoint(pos) or rgn_notch.collidepoint(pos):
                    self.pg_board_drag(evt.rel)
            if evt.buttons[0]:
                if rgn_mnmap.collidepoint(pos):
                    self.pg_minimap_set((pos[0]-v.mmx, pos[1]-v.mmy))
        elif evt.type == pg.MOUSEBUTTONDOWN:
            pos = evt.pos
            if rgn_board.collidepoint(pos) or rgn_notch.collidepoint(pos):
                if evt.button == 1: self.pg_board_lclick(pos)
            if rgn_mnmap.collidepoint(pos):
                if evt.button == 1:
                    self.pg_minimap_set((pos[0]-v.mmx, pos[1]-v.mmy))

    def pg_board_drag(self, rel):
        v = self.vars
        rel_x, rel_y = rel
        x, y = v.brx - rel_x, v.bry - rel_y
        if x < 0: x = 0
        if x > v.brw-v.emb_w: x = v.brw-v.emb_w
        if y < 0: y = 0
        if y > v.brh-v.emb_h: y = v.brh-v.emb_h
        v.brx, v.bry = x, y
        self.ig_refresh_board = True

    def pg_minimap_set(self, pos):
        '''pos (0,0) is in minimap NW corner'''
        v = self.vars
        frac_x = (pos[0]-int(v.mm_vbw//2))/v.mmh
        frac_y = (pos[1]-int(v.mm_vbh//2))/v.mmh
        x, y = int(frac_x*v.brw), int(frac_y*v.brh)
        if x < 0: x = 0
        if x > v.brw-v.emb_w: x = v.brw-v.emb_w
        if y < 0: y = 0
        if y > v.brh-v.emb_h: y = v.brh-v.emb_h
        v.brx, v.bry = x, y
        self.ig_refresh_board = True

    def pg_board_lclick(self, pos):
        v = self.vars
        x, y = pos
        x, y = (x+v.brx)//v.fct, (y+v.bry)//v.fct
        if self.pg_pointing_target:
            self.pg_set_target(x, y)
        else:
            self.pg_select(x, y)

    def pg_set_target(self):
        self.pg_pointing_target = False
        self.pg_target = x, y

    def pg_select(self, x, y):
        x, y = y, x # NOTE
        board = self.session.board
        shift = pg.key.get_mods() & pg.KMOD_LSHIFT
        if board.board[y][x].is_occupied:
            object = board.board[y][x].object
            if shift:
                if object.selected:
                    object.deselect()
                    self.selection.remove(object)
                else:
                    object.select()
                    self.selection += [object]
            else:
                self.pg_deselect_all()
                object.select()
                self.selection = [object]
        else:
            if not shift: self.pg_deselect_all()
            # Clicking with shift at empty cell does nothing
        self.sort_selection()
        self.ig_refresh_board = True

    def pg_deselect_all(self):
        for obj in self.selection:
            obj.deselect()
        self.selection = []

    def sort_selection(self):
        oldlen = len(self.selection)
        oldsel = [o for o in self.selection]
        sorted = []
        types_order = [
            'soldier', 'worker',
            'command', 'tower', 'wall',
            'woodfield', 'ironfield', 'fuelfield',
        ]
        for obj_type in types_order:
            for obj in self.selection:
                if obj.objkey == obj_type:
                    sorted += [obj]
        self.selection = sorted
        if oldlen != len(self.selection):
            l = [o.objkey for o in oldsel if o not in self.selection]
            Log.warn('Object type "'+l[0]+'" is not assigned to selection order')
