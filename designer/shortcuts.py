from kivy.core.window import Window, Keyboard
from kivy.uix.widget import Widget

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

    def do_exit(self, *args):
        d = get_designer()
        d.on_request_close()
