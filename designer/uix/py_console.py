import code
import sys
import threading

from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty,\
    StringProperty, NumericProperty, partial
from kivy.lang import Builder
try:
    from rlcompleter import Completer
except ImportError:
    Completer = None

Builder.load_string('''
<PythonConsole>:
    text_input: interactive_text_input
    scroll_view: scroll_view
    ScrollView:
        id: scroll_view
        InteractiveShellInput:
            id: interactive_text_input
            size_hint: (1, None)
            font_size: root.font_size
            foreground_color: root.foreground_color
            background_color: root.background_color
            height: max(self.parent.height, self.minimum_height)
            on_ready_to_input: root.ready_to_input()
            sh: root.sh
''')


class PseudoFile(object):
    '''A psuedo file object, to redirect I/O operations from Python Shell to
       InteractiveShellInput.
    '''

    def __init__(self, sh):
        self.sh = sh

    def write(self, s):
        '''To write to a PsuedoFile object.
        '''
        self.sh.write(s)

    def writelines(self, lines):
        '''To write lines to a PsuedoFile object.
        '''

        for line in lines:
            self.write(line)

    def flush(self):
        '''To flush a PsuedoFile object.
        '''
        pass

    def isatty(self):
        '''To determine if PsuedoFile object is a tty or not.
        '''
        return True


class Shell(code.InteractiveConsole):
    "Wrapper around Python that can filter input/output to the shell"

    def __init__(self, root):
        code.InteractiveConsole.__init__(self)
        self.thread = None
        self.root = root
        self._exit = False

    def write(self, data):
        '''write data to show as output on the screen.
        '''
        import functools
        Clock.schedule_once(functools.partial(self.root.show_output, data), 0)

    def raw_input(self, prompt=""):
        '''To show prompt and get required data from user.
        '''
        return self.root.get_input(prompt)

    def runcode(self, _code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback. All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught. The
        caller should be prepared to deal with it.

        """
        org_stdout = sys.stdout
        sys.stdout = PseudoFile(self)
        try:
            exec(_code, self.locals)
        except SystemExit:
            print('It\'s not possible to exit from Kivy Designer'
                                                    ' Python console')
        except:
            self.showtraceback()

        sys.stdout = org_stdout

    def exit(self):
        '''To exit PythonConsole.
        '''
        self._exit = True

    def interact(self, banner=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specify the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current class name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).

        """
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license"'\
            ' for more information.'
        if banner is None:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        else:
            self.write("%s\n" % str(banner))
        more = 0
        while not self._exit:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                    if line is None:
                        continue
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and isinstance(line, bytes):
                        line = line.decode(encoding)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line)

            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0


class InteractiveThread(threading.Thread):
    '''Another thread in which main loop of Shell will run.
    '''
    def __init__(self, sh):
        super(InteractiveThread, self).__init__()
        self._sh = sh
        self._sh.thread = self

    def run(self):
        '''To start main loop of _sh in this thread.
        '''
        self._sh.interact()


class InteractiveShellInput(TextInput):
    '''Displays Output and sends input to Shell. Emits 'on_ready_to_input'
       when it is ready to get input from user.
    '''

    sh = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.py_console.Shell`
       :data:`sh` is an :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_ready_to_input',)

    def __init__(self, **kwargs):
        super(InteractiveShellInput, self).__init__(**kwargs)
        self.last_line = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Override of _keyboard_on_key_down.
        '''
        if keycode[0] == 9 and Completer:
            # tab, add autocomplete suggestion
            txt = self.text[self._cursor_pos:]

            if txt.strip():
                suggestion = Completer(self.sh.locals).complete(txt, 0)
                if suggestion:
                    self.select_text(self._cursor_pos,
                                          self._cursor_pos + len(txt))
                    self.delete_selection()
                    Clock.schedule_once(
                        partial(self.insert_text, suggestion))
                return False

        elif keycode[0] == 13:
            # For enter
            self.last_line = self.text[self._cursor_pos:]
            self.dispatch('on_ready_to_input')

        return super(InteractiveShellInput, self).keyboard_on_key_down(
            window, keycode, text, modifiers)

    def insert_text(self, substring, from_undo=False):
        '''Override of insert_text
        '''
        if self.cursor_index() < self._cursor_pos:
            return

        return super(InteractiveShellInput, self).insert_text(substring,
                                                              from_undo)

    def on_ready_to_input(self, *args):
        '''Default handler of 'on_ready_to_input'
        '''
        pass

    def show_output(self, output):
        '''Show output to the user.
        '''
        self.text += output
        Clock.schedule_once(self._set_cursor_val, 0.1)

    def _set_cursor_val(self, *args):
        '''Get last position of cursor where output was added.
        '''
        self._cursor_pos = self.cursor_index()
        from kivy.animation import Animation
        anim = Animation(scroll_y=0, d=0.5)
        anim.cancel_all(self.parent)
        anim.start(self.parent)


class PythonConsole(BoxLayout):

    text_input = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.py_console.InteractiveShellInput`
       :data:`text_input` is an :class:`~kivy.properties.ObjectProperty`
    '''

    sh = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.py_console.Shell`
       :data:`sh` is an :class:`~kivy.properties.ObjectProperty`
    '''

    scroll_view = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.scrollview.ScrollView`
       :data:`scroll_view` is an :class:`~kivy.properties.ObjectProperty`
    '''

    foreground_color = ListProperty((.5, .5, .5, .93))
    '''This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(.5, .5, .5, .93)'
    '''

    background_color = ListProperty((0, 0, 0, 1))
    '''This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(0, 0, 0, 1)'''

    font_size = NumericProperty(14)
    '''Indicates the size of the font used for the console

    :data:`font_size` is a :class:`~kivy.properties.NumericProperty`,
    Default to '9'
    '''

    def __init__(self, **kwargs):
        super(PythonConsole, self).__init__()
        self.sh = Shell(self)
        self._thread = InteractiveThread(self.sh)
        self._thread.setDaemon(True)

        Clock.schedule_once(self.run_sh)
        self._ready_to_input = False
        self._exit = False

    def ready_to_input(self, *args):
        '''Specifies that PythonConsole is ready to take input from user.
        '''
        self._ready_to_input = True

    def run_sh(self, *args):
        '''Start Python Shell.
        '''
        self._thread.start()

    def show_output(self, data, dt):
        '''Show output to user.
        '''
        self.text_input.show_output(data)

    def _show_prompt(self, *args):
        '''Show prompt to user and asks for input.
        '''
        self.text_input.show_output(self.prompt)

    def get_input(self, prompt):
        '''Get input from user.
        '''
        import time
        self.prompt = prompt
        Clock.schedule_once(self._show_prompt, 0.1)
        while not self._ready_to_input and not self._exit:
            time.sleep(0.05)

        self._ready_to_input = False
        return self.text_input.last_line

    def exit(self):
        '''Exit PythonConsole
        '''
        self._exit = True
        self.sh.exit()

if __name__ == '__main__':
    runTouchApp(PythonConsole())
