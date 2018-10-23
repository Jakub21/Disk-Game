import tkinter as tk
from tkinter import ttk
import yaml
import src.ui_elems as el
import src.system as internal
from src.board import Board
from src.session import Session
from src.player import Player

import logging
Log = logging.getLogger('MainLogger')

ALL = (tk.N, tk.S, tk.E, tk.W)

class Launcher:
    def __init__(self, is_debug=False):
        Log.info('Starting launcher')
        self.leaving = False
        self.debug = is_debug
        self.starting_game = False
        self.load_config()
        self.ui_init()
        self.ui_tk_make_styles()
        self.ui_tk_make_sframe()
        self.ui_tk_make_views()
        self.ui_show_view('app_title')

    def loop(self):
        self.root.update()

    def start_game(self, board_name):
        Log.debug('Starting game')
        ####  TEMP  ####
        board_path = self.CORE.board_dir + board_name + self.CORE.board_suff
        self.session = Session(self)
        board = Board(self.session, board_path)
        self.session.set_board(board)
        self.player = Player('Local', 'temp_pwd')
        self.session.add_player(self.player)
        ################
        self.starting_game = True

    def load_config(self):
        '''Loads configuration files'''
        Log.debug('Loading config files')
        self.CORE = internal.to_ns(yaml.load(open('cnf/core.yml', 'r')))
        self.TEXT = internal.to_ns(yaml.load(open('cnf/text.yml', 'r')))
        self.CLRS = internal.to_ns(yaml.load(open('cnf/clrs.yml', 'r')))
        self.GAME = internal.to_ns(yaml.load(open('cnf/game.yml', 'r')))
        self.LNCH = internal.to_ns(yaml.load(open('cnf/lnch.yml', 'r')))
        self.USER = internal.to_ns(yaml.load(open('cnf/user.yml', 'r')))
        self.KBDS = internal.to_ns(yaml.load(open('cnf/kbds.yml', 'r')))

    def ui_init(self):
        '''Initializes tkinter UI'''
        Log.debug('Initializing UI')
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title(self.TEXT.window_title)
        self.root.iconbitmap(self.CORE.icon_path)
        w, h = self.LNCH.window_size
        self.root.geometry('{}x{}'.format(w, h))
        self.widgets = {}
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

    def ui_get_font(self, key):
        '''Returns font configuration tuple'''
        Log.debug('Requested font "{}"'.format(key))
        font_family = self.CORE.font_family
        height, is_bold = self.CORE.fonts[key]
        if is_bold: return (font_family, height, 'bold')
        else: return (font_family, height)

    def ui_get_version_text(self):
        '''Returns version text based on config'''
        return self.CORE.version_smb + ' | ' + self.CORE.version_txt

    @staticmethod
    def ui_rowcol_config(element, col_weights=[1], row_weights=[]):
        '''Configures rows and columns weights of element'''
        for col, weight in enumerate(col_weights):
            element.columnconfigure(col, weight=weight)
        for row, weight in enumerate(row_weights):
            element.rowconfigure(row, weight=weight)

    @staticmethod
    def ui_get_grid(col, row, cspan=1, rspan=1, sticky=None, padding=2):
        '''Returns keyword args dictionary for grid method of tk widgets'''
        if sticky is None: sticky = ALL
        result = {'column':col, 'row':row, 'columnspan':cspan, 'rowspan':rspan,
            'sticky':sticky}
        if padding==2: paddings={'padx':30, 'pady':10, 'ipadx':20, 'ipady':10}
        elif padding==1: paddings = {'padx':5, 'pady':5, 'ipadx':5, 'ipady':5}
        else: paddings = {}
        result.update(paddings)
        return result

    ################################
    # Menu pages and related

    def ui_tk_make_styles(self):
        '''Creates TTK styles '''
        Log.debug('Creating TTK styles')
        newstyle = ttk.Style()
        for k, v in self.LNCH.styles.items():
            Log.debug('Creating style: {}'.format(k))
            if len(v) == 3:
                newstyle.configure(k, foreground=v[0], background=v[1],
                    font=self.ui_get_font(v[2]))
            elif len(v) == 2:
                newstyle.configure(k, foreground=v[0], background=v[1])
            else:
                Log.error('Invalid style format at key {}'.format(k))
                self.quit()

    def ui_tk_make_sframe(self):
        '''Creates sframe. sframe is present in all menu-like views'''
        Log.debug('Creating sframe')
        self.sframe = ttk.Frame(self.root, style='std.TFrame')
        self.sframe.grid(sticky=ALL)
        self.widgets['title_label'] = ttk.Label(self.sframe,
            style='title.TLabel', text=self.TEXT.title_label, anchor=tk.CENTER)
        self.widgets['versn_label'] = ttk.Label(self.sframe,
            style='version.TLabel', text=self.ui_get_version_text())
        self.widgets['title_label'].grid(**self.ui_get_grid(0,0,3,1))
        self.widgets['versn_label'].grid(**self.ui_get_grid(0,2,3,1,'es',False))
        self.ui_rowcol_config(self.sframe, [0,1,0], [0,1,0])

    def ui_tk_make_views(self):
        '''Creates menu-like views'''
        Log.debug('Creating views')
        self.views = {}
        # App-title view
        self.views['app_title'] = ttk.Frame(self.sframe, style='std.TFrame')
        self.widgets['btt_app_title_play'] = el.Button(self.views['app_title'],
            'std.TButton', self.TEXT.btt_play, self.ui_show_view, 'pl_single')
        self.widgets['btt_app_title_quit'] = el.Button(self.views['app_title'],
            'std.TButton', self.TEXT.btt_quit, self.quit)
        self.widgets['btt_app_title_play'].grid(**self.ui_get_grid(0,0))
        self.widgets['btt_app_title_quit'].grid(**self.ui_get_grid(0,1))
        self.ui_rowcol_config(self.views['app_title'])
        # pl_single view
        self.views['pl_single'] = ttk.Frame(self.sframe, style='std.TFrame')
        self.widgets['btt_pl_single_start'] = el.Button(self.views['pl_single'],
            'std.TButton', self.TEXT.btt_start, self.start_game, 'first')
            # TEMP,TODO: This button should be binded to method that checks map
            # choice of user
        self.widgets['btt_pl_single_back'] = el.Button(self.views['pl_single'],
            'std.TButton', self.TEXT.btt_back, self.ui_show_view, 'app_title')
        self.widgets['btt_pl_single_start'].grid(**self.ui_get_grid(0,0))
        self.widgets['btt_pl_single_back'].grid(**self.ui_get_grid(0,1))
        self.ui_rowcol_config(self.views['pl_single'])

    def ui_show_view(self, page_key):
        '''Shows chosen view from views dictionary'''
        try:
            for key, view in self.views.items():
                view.grid_forget()
            self.views[page_key].grid(**self.ui_get_grid(1,1))
        except KeyError:
            Log.error('Invalid page key "{}"'.format(page_key))
            self.quit()

    def quit(self):
        '''Application quit method'''
        Log.info('Leaving app')
        self.leaving = True
        self.root.destroy()
