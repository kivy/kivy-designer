from kivy.core.window import Window, Keyboard

from designer.helper_functions import get_designer


class Shortcuts(object):

    def __init__(self, **kw):
        Window.bind(on_key_down=self.parse_key_down)
        # map is the link between a shortcut and a callback
        # the key is a formatted keyboard shortcuts string
        # and the value is a method declared in this class
        self.map = {}

    def map_shortcuts(self, config_parser, *args):
        '''Read shortcuts from config_parser
        :param config_parser: config parser with all shorcut settings
        '''
        g = config_parser.getdefault

        # get all defined shortcuts
        m = {
            g('shortcuts', 'new_file', ''): [self.do_new_file, 'new_file'],
            g('shortcuts', 'new_project', ''): [self.do_new_project, 'new_project'],
            g('shortcuts', 'open_project', ''): [self.do_open_project, 'open_project'],
            g('shortcuts', 'save', ''): [self.do_save, 'save'],
            g('shortcuts', 'save_as', ''): [self.do_save_as, 'save_as'],
            g('shortcuts', 'close_project', ''): [self.do_close_project, 'close_project'],
            g('shortcuts', 'recent', ''): [self.do_recent, 'recent'],
            g('shortcuts', 'settings', ''): [self.do_settings, 'settings'],
            g('shortcuts', 'exit', ''): [self.do_exit, 'exit']
        }

        self.map = m

    def parse_key_down(self, keyboard, key, codepoint, text, modifier, *args):
        '''Parse keys and generate the formatted keyboard shortcut
        '''
        key_str = Keyboard.keycode_to_string(Window._system_keyboard, key)
        modifier.sort()
        value = str(modifier) + ' + ' + key_str
        if value in self.map:
            self.map.get(value)[0]()
            return True

    def do_new_file(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_new_file
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_new_file_pressed()

    def do_new_project(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_new_project
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_new_project_pressed()

    def do_open_project(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_open_project
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_open_pressed()

    def do_save(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_save
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_save_pressed()

    def do_save_as(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_save_as
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_save_as_pressed()

    def do_close_project(self, *args):
        d = get_designer()
        btn = d.ids.actn_btn_close_proj
        menu = d.ids.actn_menu_file
        if not btn.disabled and not menu.disabled:
            d.action_btn_close_proj_pressed()

    def do_recent(self, *args):
        d = get_designer()
        d.action_btn_recent_files_pressed()

    def do_settings(self, *args):
        d = get_designer()
        d.action_btn_settings_pressed()

    def do_exit(self, *args):
        d = get_designer()
        d.on_request_close()
