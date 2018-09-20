import tkinter as tk
from tkinter import ttk
import src.ui_elems as el
from src.ingame import InGame

import logging
Log = logging.getLogger('MainLogger')

ALL = (tk.N, tk.S, tk.E, tk.W)

class Interface(InGame):
    def __init__(self):
        self.root = tk.Tk()
        self.in_ig_view = False
        self.console_h = 220
        self.ui_init()
        self.ui_set_binds()
        self.ui_toggle_fullscreen(force=self.is_fullscreen)
        self.ui_tk_make_styles()
        self.ui_tk_make_sframe()
        self.ui_tk_make_views()
        self.ui_make_ingame_view()
        super().__init__()
        self.ui_show_view('app_title')

    ################################
    # Basic UI methods

    def ui_init(self):
        '''Initializes tkinter UI'''
        Log.debug('Initializing UI')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title(self.TEXT.window_title)
        self.root.iconbitmap(self.CORE.icon_path)
        w, h = self.CORE.window_size
        self.root.geometry('{}x{}'.format(w, h))
        self.is_fullscreen = self.CORE.use_fullscreen
        self.widgets = {}

    def ui_set_binds(self):
        '''Creates binds and protocols'''
        Log.debug('Setting binds and protocols')
        self.root.bind('<F11>', self.ui_toggle_fullscreen)
        #self.root.bind('<F10>', self.ui_ig_toggle_menu) # NOTE
        self.root.protocol('WM_DELETE_WINDOW', self.quit)

    def ui_toggle_fullscreen(self, *args, force=None):
        '''Toggles fullscreen (If force param is defined sets fs as defined)'''
        Log.debug('Toggling fullscreen mode')
        if force is None:
            self.is_fullscreen = not self.is_fullscreen
            state = self.is_fullscreen
        else: state = force
        self.root.attributes('-fullscreen', state)

    def ui_get_font(self, key):
        '''Returns font configuration tuple'''
        Log.debug('Requested font "{}"'.format(key))
        font_family = self.CORE.font_family
        height, is_bold = self.CORE.fonts[key]
        if is_bold: return (font_family, height, 'bold')
        else: return (font_family, height)

    ################################
    # Helper methods

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
        for k, v in self.CORE.styles.items():
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
            'std.TButton', self.TEXT.btt_start, self.session_start, 'first')
            # TEMP,TODO: This button should be binded to method that checks map
            # choice of user
        self.widgets['btt_pl_single_back'] = el.Button(self.views['pl_single'],
            'std.TButton', self.TEXT.btt_back, self.ui_show_view, 'app_title')
        self.widgets['btt_pl_single_start'].grid(**self.ui_get_grid(0,0))
        self.widgets['btt_pl_single_back'].grid(**self.ui_get_grid(0,1))
        self.ui_rowcol_config(self.views['pl_single'])

    def ui_make_ingame_view(self):
        '''Creates in-game view (contains PyGame embed target frame)'''
        Log.debug('Creating embed view')
        self.ig_view = ttk.Frame(self.root, style='std.TFrame')
        self.ig_console = ttk.Frame(self.ig_view, style='ig.TFrame',
            height=self.console_h)
        self.pg_embed = ttk.Frame(self.ig_view, style='std.TFrame')
        self.ig_console.grid(**self.ui_get_grid(0,1, padding=0))
        self.pg_embed.grid(**self.ui_get_grid(0,0, padding=0))
        self.ui_rowcol_config(self.ig_view, [1], [1,0])
        self.pg_embed.bind('<Configure>', self.pg_update_size)

    def ui_show_view(self, page_key):
        '''Shows chosen view from views dictionary'''
        if page_key == 'game':
            self.ui_show_ig_view()
        else:
            if self.in_ig_view: ui_hide_ig_view()
            try:
                for key, view in self.views.items():
                    view.grid_forget()
                self.views[page_key].grid(**self.ui_get_grid(1,1))
            except KeyError:
                Log.error('Invalid page key "{}"'.format(page_key))
                self.quit()

    def ui_show_ig_view(self):
        '''Switch from in-game view to menu-like view'''
        Log.debug('Switching view mode')
        self.in_ig_view = True
        self.sframe.grid_forget()
        self.ig_view.grid(sticky=ALL)

    def ui_hide_ig_view(self):
        '''Switch from menu-like view to in-game view'''
        Log.debug('Switching view mode')
        self.in_ig_view = False
        self.ig_view.grid_forget()
        self.sframe.grid(sticky=ALL)
