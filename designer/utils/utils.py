'''This file contains a few functions which are required by more than one
   module of Kivy Designer.
'''
import functools
import inspect
import os
import sys

import designer
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


class FakeSettingList(EventDispatcher):
    '''Fake Kivy Setting to use SettingList
    '''

    items = ListProperty([])
    '''List with default visible items
    :attr:`items` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    allow_custom = BooleanProperty(False)
    '''Allow/disallow a custom item to the list
    :attr:`allow_custom` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    group = StringProperty(None)
    '''CheckBox group name. If the CheckBox is in a Group,
    it becomes a Radio button.
    :attr:`group` is a :class:`~kivy.properties.StringProperty` and
    defaults to ''
    '''

    desc = StringProperty(None, allownone=True)
    '''Description of the setting, rendered on the line below the title.

    :attr:`desc` is a :class:`~kivy.properties.StringProperty` and defaults to
    None.
    '''


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


def get_config_dir():
    '''This function returns kivy-designer's config dir
    '''
    user_dir = os.path.join(App.get_running_app().user_data_dir,
                            '.kivy-designer')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir


def get_kd_dir():
    '''Return kivy designer source/binaries folder
    '''
    _dir = os.path.dirname(designer.__file__)
    if isinstance(_dir, bytes):
        _dir = _dir.decode(get_fs_encoding())
    return _dir


def get_kd_data_dir():
    '''Return kivy designer's data path
    '''
    return os.path.join(get_kd_dir(), 'data')


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
    d = get_designer()
    d.statusbar.show_message(*args, **kwargs)


def update_info(*args, **kwargs):
    '''Shortcut to display an update on status info
    '''
    d = get_designer()
    d.statusbar.update_info(*args, **kwargs)


def show_error_console(text, append=False):
    '''Shows a text on Error Console.
    :param text: error message
    :param append appends the new text at the bottom of console
    '''
    d = get_designer()
    error_console = d.ui_creator.error_console
    if append:
        text = error_console.text + text
    error_console.text = text


def get_designer():
    '''Return the Designer instance
    '''
    return App.get_running_app().root


def get_current_project():
    '''Returns the current project in project_manager.
    '''
    d = get_designer()
    return d.project_manager.current_project


def ignore_proj_watcher(f):
    '''Function decorator to makes project watcher ignores file modification
    '''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        watcher = get_designer().project_watcher
        watcher.pause_watching()
        f(*args, **kwargs)
        return watcher.resume_watching()
    return wrapper


def get_app_widget(target, **default_args):
    '''Creates a widget instance by it's name and module
    :param target: instance of designer.project_manager.AppWidget
    '''
    d = get_designer()
    if target.is_dynamic:
        name = target.name.split('@')[0]
        with d.ui_creator.playground.sandbox:
            return Factory.get(name)(**default_args)
    elif target.is_root:
        return target.instance
    else:
        classes = inspect.getmembers(sys.modules[target.module_name],
                                     inspect.isclass)
        for klass_name, klass in classes:
            if issubclass(klass, Widget) and klass_name == target.name:
                with d.ui_creator.playground.sandbox:
                    return klass(**default_args)

        return None


def widget_contains(container, child):
    '''Search recursively for child in container
    :param container: container widget
    :param child: item to search
    '''
    if container == child:
        return True
    for w in container.children:
        if widget_contains(w, child):
            return True
    return False


def get_fs_encoding():
    encoding = sys.getfilesystemencoding()
    if not encoding:
        encoding = sys.stdin.encoding
    if not encoding:
        encoding = sys.getdefaultencoding()
    return encoding
