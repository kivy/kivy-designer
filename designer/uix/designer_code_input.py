import re

from kivy import Config
from kivy.utils import get_color_from_hex
from pygments import styles, highlight
from designer.helper_functions import show_alert
from kivy.uix.codeinput import CodeInput
from kivy.properties import BooleanProperty, Clock, partial


class DesignerCodeInput(CodeInput):
    '''A subclass of CodeInput to be used for KivyDesigner.
       It has copy, cut and paste functions, which otherwise are accessible
       only using Keyboard.
       It emits on_show_edit event whenever clicked, this is catched
       to show EditContView;
    '''

    __events__ = ('on_show_edit',)

    clicked = BooleanProperty(False)
    '''If clicked is True, then it confirms that this widget has been clicked.
       The one checking this property, should set it to False.
       :data:`clicked` is a :class:`~kivy.properties.BooleanProperty`
    '''

    def __init__(self, **kwargs):
        super(DesignerCodeInput, self).__init__(**kwargs)
        parser = Config.get_configparser('DesignerSettings')
        if parser:
            parser.add_callback(self.on_codeinput_theme,
                                'global', 'code_input_theme')
            self.style_name = parser.getdefault('global', 'code_input_theme',
                                                'emacs')

    def on_codeinput_theme(self, section, key, value, *args):
        if not value in styles.get_all_styles():
            show_alert("Error", "This theme is not available")
        else:
            self.style_name = value

    def on_style_name(self, *args):
        super(DesignerCodeInput, self).on_style_name(*args)
        self.background_color = get_color_from_hex(self.style.background_color)
        self._trigger_refresh_text()

    def on_show_edit(self, *args):
        pass

    def on_touch_down(self, touch):
        '''Override of CodeInput's on_touch_down event.
           Used to emit on_show_edit
        '''
        if self.collide_point(*touch.pos):
            self.clicked = True
            self.dispatch('on_show_edit')

        return super(DesignerCodeInput, self).on_touch_down(touch)

    def _do_focus(self, *args):
        '''Force the focus on this widget
        '''
        self.focus = True

    def do_select_all(self, *args):
        '''Function to select all text
        '''
        self.select_all()

    def find_next(self, search, use_regex=False, case=False):
        '''Find the next occurrence of the string according to the cursor
        position
        '''
        text = self.text
        if not case:
            text = text.upper()
            search = search.upper()
        lines = text.splitlines()

        col = self.cursor_col
        row = self.cursor_row

        found = -1
        size = 0  # size of string before selection
        line = None
        search_size = len(search)

        for i, line in enumerate(lines):
            if i >= row:
                if use_regex:
                    if i == row:
                        line_find = line[col + 1:]
                    else:
                        line_find = line[:]
                    found = re.search(search, line_find)
                    if found:
                        search_size = len(found.group(0))
                        found = found.start()
                    else:
                        found = -1
                else:
                    # if on current line, consider col
                    if i == row:
                        found = line.find(search, col + 1)
                    else:
                        found = line.find(search)
                # has found the string. found variable indicates the initial po
                if found != -1:
                    self.cursor = (found, i)
                    break
            size += len(line)

        if found != -1:
            pos = text.find(line) + found
            self.select_text(pos, pos + search_size)

    def find_prev(self, search, use_regex=False, case=False):
        '''Find the previous occurrence of the string according to the cursor
        position
        '''
        text = self.text
        if not case:
            text = text.upper()
            search = search.upper()
        lines = text.splitlines()

        col = self.cursor_col
        row = self.cursor_row
        lines = lines[:row + 1]
        lines.reverse()
        line_number = len(lines)

        found = -1
        line = None
        search_size = len(search)

        for i, line in enumerate(lines):
            i = line_number - i - 1
            if use_regex:
                if i == row:
                    line_find = line[:col]
                else:
                    line_find = line[:]
                found = re.search(search, line_find)
                if found:
                    search_size = len(found.group(0))
                    found = found.start()
                else:
                    found = -1
            else:
                # if on current line, consider col
                if i == row:
                    found = line[:col].find(search)
                else:
                    found = line.find(search)
            # has found the string. found variable indicates the initial po
            if found != -1:
                self.cursor = (found, i)
                break

        if found != -1:
            pos = text.find(line) + found
            self.select_text(pos, pos + search_size)
