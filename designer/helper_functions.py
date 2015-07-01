'''This file contains a few functions which are required by more than one
   module of Kivy Designer.
'''
import functools

import os

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def get_indent_str(indentation):
    '''Return a string consisting only indentation number of spaces
    '''
    i = 0
    s = ''
    while i < indentation:
        s += ' '
        i += 1

    return s


def get_line_end_pos(string, line):
    '''Returns the end position of line in a string
    '''
    _line = 0
    _line_pos = -1
    _line_pos = string.find('\n', _line_pos + 1)
    while _line < line:
        _line_pos = string.find('\n', _line_pos + 1)
        _line += 1

    return _line_pos


def get_line_start_pos(string, line):
    '''Returns starting position of line in a string
    '''
    _line = 0
    _line_pos = -1
    _line_pos = string.find('\n', _line_pos + 1)
    while _line < line - 1:
        _line_pos = string.find('\n', _line_pos + 1)
        _line += 1

    return _line_pos


def get_indent_level(string):
    '''Returns the indentation of first line of string
    '''
    lines = string.splitlines()
    lineno = 0
    line = lines[lineno]
    indent = 0
    total_lines = len(lines)
    while line < total_lines and indent == 0:
        indent = len(line) - len(line.lstrip())
        line = lines[lineno]
        line += 1

    return indent


def get_indentation(string):
    '''Returns the number of indent spaces in a string
    '''
    count = 0
    for s in string:
        if s == ' ':
            count += 1
        else:
            return count

    return count


def get_kivy_designer_dir():
    '''This function returns kivy-designer's config dir
    '''
    user_dir = os.path.join(App.get_running_app().user_data_dir,
                            '.kivy-designer')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir


def show_alert(title, msg, width=500, height=200):
    lbl_message = Label(text=msg)
    lbl_message.padding = [10, 10]
    popup = Popup(title=title,
                        content=lbl_message,
                        size_hint=(None, None),
                        size=(width, height))
    popup.open()


def show_message(*args, **kwargs):
    '''Shortcut to display a message on status bar
    '''
    App.get_running_app().root.statusbar.show_message(*args, **kwargs)


def get_designer():
    '''Return the Designer instance
    '''
    return App.get_running_app().root


def ignore_proj_watcher(f):
    '''Function decorator to makes project watcher ignores file modification
    '''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        watcher = App.get_running_app().root.project_watcher
        watcher.stop()
        f(*args, **kwargs)
        return watcher.resume_watching()
    return  wrapper
