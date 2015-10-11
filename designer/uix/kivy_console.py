# -*- coding: utf-8 -*-
'''
KivyConsole
===========

.. image:: images/KivyConsole.jpg
    :align: right

:class:`KivyConsole` is a :class:`~kivy.uix.widget.Widget`
Purpose: Providing a system console for debugging kivy by running another
instance of kivy in this console and displaying it's output.
To configure, you can use

cached_history  :
cached_commands :
font_size       :
shell           :

''Versionadded:: 1.0.?TODO

''Usage:
    from kivy.uix.kivyconsole import KivyConsole

    parent.add_widget(KivyConsole())

or

    console = KivyConsole()

To run a command:

    console.stdin.write('ls -l')

or
    subprocess.Popen(('echo','ls'), stdout = console.stdin)

To display something on stdout write to stdout

    console.stdout.write('this will be written to the stdout\n')

or
    subprocess.Popen('ps', stdout = console.stdout, shell = True)

Warning: To read from stdout remember that the process is run in a thread, give
it time to complete otherwise you might get a empty or partial string;
returning whatever has been written to the stdout pipe till the time
read() was called.

    text = console.stdout.read() or read(no_of_bytes) or readline()

TODO: create a stdin and stdout pipe for
      this console like in logger.[==== ]%done
TODO: move everything that is non-specific to
      a generic console in a different Project.[     ]%done
TODO: Fix Prompt, make it smaller plus give it more info

''Shortcuts:
Inside the console you can use the following shortcuts:
Shortcut                     Function
_________________________________________________________
PGup           Search for previous command inside command history
               starting with the text before current cursor position

PGdn           Search for Next command inside command history
               starting with the text before current cursor position

UpArrow        Replace command_line with previous command

DnArrow        Replace command_line with next command
               (only works if one is not at last command)

Tab            If there is nothing before the cursur when tab is pressed
                   contents of current directory will be displayed.
               '.' before cursur will be converted to './'
               '..' to '../'
               If there is a path before cursur position
                   contents of the path will be displayed.
               else contents of the path before cursor containing
                    the commands matching the text before cursur will
                    be displayed
'''

__all__ = ('KivyConsole', )

import shlex
import subprocess
import re
try:
    import thread
except ImportError:
    import _thread as thread
import os
import sys
from functools import partial
from pygments.lexers import BashSessionLexer

from kivy.uix.gridlayout import GridLayout
from kivy.properties import (NumericProperty, StringProperty,
                             BooleanProperty, ObjectProperty, DictProperty,
                             ListProperty)
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import runTouchApp
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import platform


Builder.load_string('''
<KivyConsole>:
    cols:1
    txtinput_history_box: history_box.__self__
    txtinput_command_line: command_line.__self__
    ScrollView:
        CodeInput:
            id: history_box
            size_hint: (1, None)
            height: 801
            font_size: root.font_size
            readonly: True
            foreground_color: root.foreground_color
            background_color: root.background_color
            on_text: root.on_text(*args)
    TextInput:
        id: command_line
        multiline: False
        size_hint: (1, None)
        font_size: root.font_size
        readonly: root.readonly
        foreground_color: root.foreground_color
        background_color: root.background_color
        height: 36
        on_text_validate: root.on_enter(*args)
        on_touch_up:
            self.collide_point(*args[1].pos)\\
            and root._move_cursor_to_end(self)
''')


class KivyConsole(GridLayout):
    '''This is a Console widget used for debugging and running external
    commands

    '''

    readonly = BooleanProperty(False)
    '''This defines whether a person can enter commands in the console

    :data:`readonly` is an :class:`~kivy.properties.BooleanProperty`,
    Default to 'False'
    '''

    foreground_color = ListProperty((1, 1, 1, 1))
    '''This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(1, 1, 1, 1)'
    '''

    background_color = ListProperty((0, 0, 0, 1))
    '''This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(0, 0, 0, 1)'
    '''

    cached_history = NumericProperty(200)
    '''Indicates the No. of lines to cache. Defaults to 200

    :data:`cached_history` is an :class:`~kivy.properties.NumericProperty`,
    Default to '200'
    '''

    cached_commands = NumericProperty(90)
    '''Indicates the no of commands to cache. Defaults to 90

    :data:`cached_commands` is a :class:`~kivy.properties.NumericProperty`,
    Default to '90'
    '''

    environment = DictProperty(os.environ.copy())
    '''Indicates the environment the commands are run in. Set your PATH or
    other environment variables here. like so::

        kivy_console.environment['PATH']='path'

    environment is :class:`~kivy.properties.DictProperty`, defaults to
    the environment for the pricess running Kivy console
    '''

    font_size = NumericProperty(14)
    '''Indicates the size of the font used for the console

    :data:`font_size` is a :class:`~kivy.properties.NumericProperty`,
    Default to '9'
    '''

    textcache = ListProperty(['', ])
    '''Indicates the cache of the commands and their output

    :data:`textcache` is a :class:`~kivy.properties.ListProperty`,
    Default to ''
    '''

    shell = BooleanProperty(False)
    '''Indicates the whether system shell is used to run the commands

    :data:`shell` is a :class:`~kivy.properties.BooleanProperty`,
    Default to 'False'

    WARNING: Shell = True is a security risk and therefore = False by default,
    As a result with shell = False some shell specific commands and
    redirections
    like 'ls |grep lte' or dir >output.txt will not work.
    If for some reason you need to run such commands, try running the platform
    shell first
    eg:  /bin/sh ...etc on nix platforms and cmd.exe on windows.
    As the ability to interact with the running command is built in,
    you should be able to interact with the native shell.

    Shell = True, should be set only if absolutely necessary.
    '''

    txtinput_command_line = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.register_event_type('on_subprocess_done')
        self.register_event_type('on_command_list_done')
        super(KivyConsole, self).__init__(**kwargs)
        # initialisations
        self.txtinput_command_line_refocus = False
        self.txtinput_run_command_refocus = False
        self.win = None
        self.scheduled = False
        self.command_history = []
        self.command_history_pos = 0
        self.command_status = 'closed'
        if sys.version_info >= (3, 0):
            self.cur_dir = os.getcwd()
        else:
            self.cur_dir = os.getcwdu()
        self.command_list = []  # list of cmds to be executed
        self.stdout = std_in_out(self, 'stdout')
        self.stdin = std_in_out(self, 'stdin')
        self.popen_obj = None
        # self.stderror = stderror(self)
        # delayed initialisation
        Clock.schedule_once(self._initialize)
        self_change_txtcache = self._change_txtcache
        _trig = Clock.create_trigger(self_change_txtcache)
        self.bind(textcache=_trig)
        self._hostname = 'unknown'
        try:
            if hasattr(os, 'uname'):
                self._hostname = os.uname()[1]
            else:
                self._hostname = os.environ.get('COMPUTERNAME', 'unknown')
        except Exception:
            pass
        self._username = os.environ.get('USER', '')
        if not self._username:
            self._username = os.environ.get('USERNAME', 'unknown')

    def run_command(self, command, *args):
        '''Run a command using Kivy Console.
        The output will be visible in the Kivy console.
        Returns False if there is a command running and stops. Otherwise
        start the execution of the commands and returns True
        '''
        if self.popen_obj:
            return False

        if isinstance(command, list):
            self.command_list = command
        else:
            self.command_list = [command]
        self._run_command_list()

        return True

    def _run_command_list(self, *kwargs):
        '''Runs a list of commands
        '''
        if self.command_list:
            self.stdin.write(self.command_list.pop(0))
            self.bind(on_subprocess_done=self._run_command_list)
        else:
            self.dispatch('on_command_list_done')

    def clear(self, *args):
        '''Clear the Kivy Console area
        '''
        self.txtinput_history_box.text = ''
        self.textcache = ['', ]

    def _initialize(self, dt):
        '''Set console default variable values
        '''
        cl = self.txtinput_command_line
        self.txtinput_history_box.lexer = BashSessionLexer()
        self.txtinput_history_box.text = u''.join(self.textcache)
        self.txtinput_command_line.text = self.prompt()
        self.txtinput_command_line.bind(focus=self.on_focus)
        self.txtinput_command_line.bind(
            selection_text=self.on_txtinput_selection)
        Clock.schedule_once(self._change_txtcache)
        self._focus(self.txtinput_command_line)
        self._list = [self.txtinput_command_line]

    def on_txtinput_selection(self, *args):
        '''Callback to command input text selection.
        Cannot select the PS1 variable, so it'll handle to select only
        input text.
        '''
        ticl = self.txtinput_command_line
        col = len(self.prompt())
        ticl.select_text(col, len(ticl.text))

    def _move_cursor_to_end(self, instance):
        '''Moves the command input cursor to the end
        '''
        def mte(*l):
            instance.cursor = instance.get_cursor_from_index(len_prompt)
        len_prompt = len(self.prompt())
        if instance.cursor[0] < len_prompt:
            Clock.schedule_once(mte, -1)

    def _focus(self, widg, t_f=True):
        Clock.schedule_once(partial(self._deffered_focus, widg, t_f))

    def _deffered_focus(self, widg, t_f, dt):
        if widg.get_root_window():
            widg.focus = t_f

    def prompt(self, *args):
        '''Returns the PS1 variable
        '''
        return "[%s@%s %s]>> " % (
            self._username, self._hostname,
            os.path.basename(str(self.cur_dir)))

    def _change_txtcache(self, *args):
        '''Update the Kivy Console output area
        '''
        tihb = self.txtinput_history_box
        tihb.text = ''.join(self.textcache)
        if not self.get_root_window():
            return
        tihb.height = max(tihb.minimum_height, tihb.parent.height)
        tihb.parent.scroll_y = 0

    def on_text(self, instance, txt):
        # check if history_box has more text than indicated buy
        # self.cached_history and remove excess lines from top
        if txt == '':
            return
        try:
            # self._skip_textcache = True
            self.textcache = self.textcache[-self.cached_history:]
        except IndexError:
            pass
            # self._skip_textcache = False

    def on_key_down(self, *l):
        '''Handle the on_key_down from keyboard
        '''
        ticl = self.txtinput_command_line

        def move_cursor_to(col):
            '''Update the cursor position
            '''
            ticl.cursor =\
                col, ticl.cursor[1]

        def search_history(up_dn):
            if up_dn == 'up':
                plus_minus = -1
            else:
                plus_minus = 1
            l_curdir = len(self.prompt())
            col = ticl.cursor_col
            command = ticl.text[l_curdir: col]
            max_len = len(self.command_history) - 1
            chp = self.command_history_pos

            while max_len >= 0:
                if plus_minus == 1:
                    if self.command_history_pos > max_len - 1:
                        self.command_history_pos = max_len
                        return
                else:
                    if self.command_history_pos <= 0:
                        self.command_history_pos = max_len
                        return
                self.command_history_pos = self.command_history_pos\
                    + plus_minus
                cmd = self.command_history[self.command_history_pos]
                if cmd[:len(command)] == command:
                    ticl.text = u''.join((
                        self.prompt(), cmd))
                    move_cursor_to(col)
                    return
            self.command_history_pos = max_len + 1

        if ticl.focus:
            if l[1] == 273:
                # up arrow: display previous command
                if self.command_history_pos > 0:
                    self.command_history_pos = self.command_history_pos - 1
                    ticl.text = u''.join(
                        (self.prompt(),
                         self.command_history[self.command_history_pos]))
                return
            if l[1] == 274:
                # dn arrow: display next command
                if self.command_history_pos < len(self.command_history) - 1:
                    self.command_history_pos = self.command_history_pos + 1
                    ticl.text = u''.join(
                        (self.prompt(),
                         self.command_history[self.command_history_pos]))
                else:
                    self.command_history_pos = len(self.command_history)
                    ticl.text = self.prompt()
                col = len(ticl.text)
                move_cursor_to(col)
                return
            if l[1] == 9:
                # tab: autocomplete
                def display_dir(cur_dir, starts_with=None):
                    # display contents of dir from cur_dir variable
                    starts_with_is_not_None = starts_with is not None
                    try:
                        dir_list = os.listdir(cur_dir)
                    except OSError as err:
                        self.add_to_cache(u''.join((err.strerror, '\n')))
                        return
                    if starts_with_is_not_None:
                        len_starts_with = len(starts_with)
                    self.add_to_cache(u''.join(('contents of directory: ',
                                                cur_dir, '\n')))
                    txt = u''
                    no_of_matches = 0
                    for _file in dir_list:
                        if starts_with_is_not_None:
                            if _file[:len_starts_with] == starts_with:
                                # if file matches starts with
                                txt = u''.join((txt, _file, ' '))
                                no_of_matches += 1
                        else:
                            self.add_to_cache(u''.join((_file, '\t')))
                    if no_of_matches == 1:
                        len_txt = len(txt) - 1
                        cmdl_text = ticl.text
                        len_cmdl = len(cmdl_text)
                        os_sep = os.sep \
                            if col == len_cmdl or (col < len_cmdl and
                                                   cmdl_text[col] !=
                                                   os.sep) else ''
                        ticl.text = u''.join(
                            (self.prompt(), text_before_cursor,
                             txt[len_starts_with:len_txt], os_sep,
                             cmdl_text[col:]))
                        move_cursor_to(col + (len_txt - len_starts_with) + 1)
                    elif no_of_matches > 1:
                        self.add_to_cache(txt)
                    self.add_to_cache('\n')

                # send back space to command line -remove the tab
                Clock.schedule_once(ticl.do_backspace, 0)
                l_curdir = len(self.prompt())
                move_cursor_to(l_curdir + len(ticl.text))
                ntext = os.path.expandvars(ticl.text)
                # store text before cursor for comparison
                col = ticl.cursor_col
                if ntext != ticl.text:
                    ticl.text = ntext
                    col = len(ntext)
                text_before_cursor = ticl.text[l_curdir: col]

                # if empty or space before: list cur dir
                if text_before_cursor == ''\
                   or ticl.text[col - 1] == ' ':
                    display_dir(self.cur_dir)
                # if in mid command:
                else:
                    # list commands in PATH starting with text before cursor
                    # split command into path till the seperator
                    cmd_start = text_before_cursor.rfind(' ')
                    cmd_start += 1
                    cur_dir = self.cur_dir\
                        if text_before_cursor[cmd_start] != os.sep\
                        else os.sep
                    os_sep = os.sep if cur_dir != os.sep else ''
                    cmd_end = text_before_cursor.rfind(os.sep)
                    len_txt_bef_cur = len(text_before_cursor) - 1
                    if cmd_end == len_txt_bef_cur:
                        # display files in path
                        if text_before_cursor[cmd_start] == os.sep:
                            cmd_start += 1
                        display_dir(u''.join((cur_dir, os_sep,
                                    text_before_cursor[cmd_start:cmd_end])))
                    elif text_before_cursor[len_txt_bef_cur] == '.':
                        # if / already there return
                        if len(ticl.text) > col\
                           and ticl.text[col] == os.sep:
                            return
                        if text_before_cursor[len_txt_bef_cur - 1] == '.':
                            len_txt_bef_cur -= 1
                        if text_before_cursor[len_txt_bef_cur - 1]\
                           not in (' ', os.sep):
                            return
                        # insert at cursor os.sep: / or \
                        ticl.text = u''.join((self.prompt(),
                                              text_before_cursor, os_sep,
                                              ticl.text[col:]))
                    else:
                        if cmd_end < 0:
                            cmd_end = cmd_start
                        else:
                            cmd_end += 1
                        display_dir(u''.join((
                                    cur_dir,
                                    os_sep,
                                    text_before_cursor[cmd_start:cmd_end])),
                                    text_before_cursor[cmd_end:])
                return
            if l[1] == 280:
                # pgup: search last command starting with...
                search_history('up')
                return
            if l[1] == 281:
                # pgdn: search next command starting with...
                search_history('dn')
                return
            if l[1] == 278:
                # Home: cursor should not go to the left of cur_dir
                col = len(self.prompt())
                move_cursor_to(col)
                if len(l[4]) > 0 and l[4][0] == 'shift':
                    ticl.selection_to = col
                return
            if l[1] == 276 or l[1] == 8:
                # left arrow/bkspc: cursor should not go left of cur_dir
                col = len(self.prompt())
                if ticl.cursor_col < col:
                    if l[1] == 8:
                        ticl.text = self.prompt()
                    move_cursor_to(col)
                return

    def on_focus(self, instance, value):
        '''Handle the focus on the command input
        '''
        if value:
            # focused
            if instance is self.txtinput_command_line:
                Window.unbind(on_key_down=self.on_key_down)
                Window.bind(on_key_down=self.on_key_down)
        else:
            # defocused
            Window.unbind(on_key_down=self.on_key_down)
            if self.txtinput_command_line_refocus:
                self.txtinput_command_line_refocus = False
                if self.txtinput_command_line.get_root_window():
                    self.txtinput_command_line.focus = True
                self.txtinput_command_line.scroll_x = 0
            if self.txtinput_run_command_refocus:
                self.txtinput_run_command_refocus = False
                instance.focus = True
                instance.scroll_x = 0
                instance.text = u''

    def add_to_cache(self, _string):
        # os.write(self.stdout.stdout_pipe, _string.encode('utf-8'))
        # self.stdout.flush()
        self.textcache.append(_string)
        _string = None

    def kill_process(self, *l):
        if self.popen_obj:
            self.popen_obj.kill()

    def on_enter(self, *l):
        '''When the user press enter and wants to run a command
        '''
        self.unbind(on_subprocess_done=self.on_enter)
        if self.command_status == 'started':
            self.kill_process()
            self.bind(on_subprocess_done=self.on_enter)
            return

        txtinput_command_line = self.txtinput_command_line
        add_to_cache = self.add_to_cache
        command_history = self.command_history

        def remove_command_interaction_widgets(*l):
            '''command finished:remove widget responsible for interaction
            '''
            parent.remove_widget(self.interact_layout)
            self.interact_layout = None
            # enable running a new command
            try:
                parent.add_widget(self.txtinput_command_line)
            except:
                self._initialize(0)

            self._focus(txtinput_command_line, True)
            Clock.schedule_once(self._change_txtcache, -1)
            self.command_status = 'closed'
            self.dispatch('on_subprocess_done')

        def run_cmd(*l):
            '''Run the command
            '''
            # this is run inside a thread so take care, avoid gui ops
            try:
                _posix = True
                if sys.platform[0] == 'w':
                    _posix = False
                cmd = shlex.split(str(command), posix=_posix)\
                    if not self.shell else command
            except Exception as err:
                cmd = ''
                self.add_to_cache(u''.join((str(err), ' <', command, ' >\n')))
            if len(cmd) > 0:
                prev_stdout = sys.stdout
                sys.stdout = self.stdout
                try:
                    # execute command
                    self.popen_obj = popen = subprocess.Popen(
                        cmd,
                        bufsize=0,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        preexec_fn=None,
                        close_fds=False,
                        shell=self.shell,
                        cwd=self.cur_dir,
                        env=self.environment,
                        universal_newlines=False,
                        startupinfo=None,
                        creationflags=0)
                    popen_stdout_r = popen.stdout.readline
                    popen_stdout_flush = popen.stdout.flush
                    txt = popen_stdout_r()
                    plat = platform()
                    while txt != '':
                        # skip flush on android
                        if plat[0] != 'a':
                            popen_stdout_flush()
                        add_to_cache(txt.decode('utf8'))
                        txt = popen_stdout_r()
                except (OSError, ValueError) as err:
                    add_to_cache(u''.join((str(err.strerror),
                                           ' < ', command, ' >\n')))
                    self.command_status = 'closed'
                sys.stdout = prev_stdout
            self.popen_obj = None
            Clock.schedule_once(remove_command_interaction_widgets, 0)

        # append text to textcache
        add_to_cache(u''.join((self.txtinput_command_line.text, '\n')))
        command = txtinput_command_line.text[len(self.prompt()):]

        if command == '':
            self.txtinput_command_line_refocus = True
            return

        # store command in command_history
        if self.command_history_pos > 0:
            self.command_history_pos = len(command_history)
            if command_history[self.command_history_pos - 1] != command:
                command_history.append(command)
        else:
            command_history.append(command)

        len_command_history = len(command_history)
        self.command_history_pos = len(command_history)

        # on reaching limit(cached_lines) pop first command
        if len_command_history >= self.cached_commands:
            self.command_history = command_history[1:]

        # replce $PATH with
        command = os.path.expandvars(command)

        # if command = cd change directory
        if command == 'clear' or command == 'cls':
            self.clear()
            txtinput_command_line.text = self.prompt()
            self.txtinput_command_line_refocus = True
            self.command_status = 'closed'
            self.dispatch('on_subprocess_done')
            return
        if command.startswith('cd ') or command.startswith('export '):
            if command[0] == 'e':
                e_q = command[7:].find('=')
                _exprt = command[7:]
                if e_q:
                    os.environ[_exprt[:e_q]] = _exprt[e_q + 1:]
                    self.environment = os.environ.copy()
            else:
                try:
                    command = re.sub('[ ]+', ' ', command)
                    if command[3] == os.sep:
                        os.chdir(command[3:])
                    else:
                        os.chdir(self.cur_dir + os.sep + command[3:])
                    if sys.version_info >= (3, 0):
                        self.cur_dir = os.getcwd()
                    else:
                        self.cur_dir = os.getcwdu()
                except OSError as err:
                    Logger.debug('Shell Console: err:' + err.strerror +
                                 ' directory:' + command[3:])
                    add_to_cache(u''.join((err.strerror, '\n')))
            txtinput_command_line.text = self.prompt()
            self.txtinput_command_line_refocus = True
            self.command_status = 'closed'
            self.dispatch('on_subprocess_done')
            return

        txtinput_command_line.text = self.prompt()
        # store output in textcache
        parent = txtinput_command_line.parent
        # disable running a new command while and old one is running
        parent.remove_widget(txtinput_command_line)
        # add widget for interaction with the running command
        txtinput_run_command = TextInput(multiline=False,
                                         font_size=self.font_size)

        def interact_with_command(*l):
            '''Text input to interact with the running command
            '''
            popen_obj = self.popen_obj
            if not popen_obj:
                return
            txt = l[0].text + u'\n'
            popen_obj_stdin = popen_obj.stdin
            popen_obj_stdin.write(txt)
            popen_obj_stdin.flush()
            self.txtinput_run_command_refocus = True

        self.txtinput_run_command_refocus = False
        txtinput_run_command.bind(on_text_validate=interact_with_command)
        txtinput_run_command.bind(focus=self.on_focus)
        btn_kill = Button(text="Stop",
                          width=60,
                          size_hint=(None, 1))

        self.interact_layout = il = GridLayout(rows=1, cols=2, height=27,
                                               size_hint=(1, None))
        btn_kill.bind(on_press=self.kill_process)
        il.add_widget(txtinput_run_command)
        il.add_widget(btn_kill)
        parent.add_widget(il)

        txtinput_run_command.focus = True
        self.command_status = 'started'
        thread.start_new_thread(run_cmd, ())

    def on_subprocess_done(self, *args):
        '''Event handler for when a process was killed
        or just finished the execution.
        '''
        pass

    def on_command_list_done(self, *args):
        '''Event handler for when the whole command list was executed or killed
        '''
        pass


class std_in_out(object):
    ''' class for writing to/reading from this console'''

    def __init__(self, obj, mode='stdout'):
        self.obj = obj
        self.mode = mode
        self.stdin_pipe, self.stdout_pipe = os.pipe()
        thread.start_new_thread(self.read_from_in_pipe, ())
        self.textcache = None

    def update_cache(self, text_line, obj, *l):
        '''Update the output text area
        '''
        obj.textcache.append(text_line)

    def read_from_in_pipe(self, *l):
        '''Read the output from the command
        '''
        txt = '\n'
        txt_line = ''
        os_read = os.read
        self_stdin_pipe = self.stdin_pipe
        self_mode = self.mode
        self_write = self.write
        Clock_schedule_once = Clock.schedule_once
        self_update_cache = self.update_cache
        self_flush = self.flush
        obj = self.obj
        try:
            while txt != '':
                txt = os_read(self_stdin_pipe, 1)
                txt_line = u''.join((txt_line, txt))
                if txt == '\n':
                    if self_mode == 'stdin':
                        # run command
                        self_write(txt_line)
                    else:
                        Clock_schedule_once(
                            partial(self_update_cache, txt_line, obj), 0)
                        self_flush()
                    txt_line = ''
        except OSError as e:
            Logger.exception(e)

    def close(self):
        '''Close the pipes
        '''
        os.close(self.stdin_pipe)
        os.close(self.stdout_pipe)

    def __del__(self):
        self.close()

    def fileno(self):
        return self.stdout_pipe

    def write(self, s):
        '''Write a command to the pipe
        '''
        Logger.debug('write called with command:' + str(s))
        if self.mode == 'stdout':
            self.obj.add_to_cache(s)
            self.flush()
        else:
            # process.stdout.write ...run command
            if self.mode == 'stdin':
                self.obj.txtinput_command_line.text = ''.join((
                    self.obj.prompt(), s))
                self.obj.on_enter()

    def read(self, no_of_bytes=0):
        if self.mode == 'stdin':
            # stdin.read
            Logger.exception('KivyConsole: can not read from a stdin pipe')
            return
        # process.stdout/in.read
        txtc = self.textcache
        if no_of_bytes == 0:
            # return all data
            if txtc is None:
                self.flush()
            while self.obj.command_status != 'closed':
                pass
            txtc = self.textcache
            return txtc
        try:
            self.textcache = txtc[no_of_bytes:]
        except IndexError:
            self.textcache = txtc
        return txtc[:no_of_bytes]

    def readline(self):
        if self.mode == 'stdin':
            # stdin.readline
            Logger.exception('KivyConsole: can not read from a stdin pipe')
            return
        else:
            # process.stdout.readline
            if self.textcache is None:
                self.flush()
            txt = self.textcache
            x = txt.find('\n')
            if x < 0:
                Logger.Debug('console_shell: no more data')
                return
            self.textcache = txt[x:]
            # ##self. write to ...
            return txt[:x]

    def flush(self):
        self.textcache = u''.join(self.obj.textcache)
        return


if __name__ == '__main__':
    runTouchApp(KivyConsole())
