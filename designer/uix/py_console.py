import code, sys, threading

from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.base import EventLoop
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.lang import Builder

Builder.load_string('''
<PythonConsole>:
    text_input: text_input2
    scroll_view: scroll_view
    ScrollView:
        id: scroll_view
        InteractiveShellInput:
            id: text_input2
            size_hint: (1, None)
            font_name: root.font_name
            font_size: root.font_size
            foreground_color: root.foreground_color
            background_color: root.background_color
            height: max(self.parent.height, self.minimum_height)
            on_ready_to_input: root.ready_to_input()
''')

class PseudoFile(object): 
    '''A psuedo file object, to redirect I/O operations from Python Shell to
       InteractiveShellInput.
    '''
    
    def __init__(self, sh):
        self.sh = sh

    def write(self, s):
        self.sh.write(s)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        pass

    def isatty(self):
        return True

class Shell(code.InteractiveConsole):
    "Wrapper around Python that can filter input/output to the shell"

    def __init__(self, root):
        code.InteractiveConsole.__init__(self)
        self.thread = None
        self.root = root
        self._exit = False

    def write(self, data):
        import functools
        Clock.schedule_once(functools.partial(self.root.show_output, data), 0)

    def push(self, line):
        return code.InteractiveConsole.push(self, line)
    
    def raw_input(self, prompt=""):
        return self.root.get_input(prompt)
    
    def runcode(self, _code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        """
        org_stdout = sys.stdout
        sys.stdout = PseudoFile(self)
        try:
            exec _code in self.locals
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            if code.softspace(sys.stdout, 0):
                print

        sys.stdout = org_stdout
    
    def exit(self):
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
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
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
                    if line == None:
                        continue
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and not isinstance(line, unicode):
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
        self._sh.interact()


class InteractiveShellInput(TextInput):
    '''Displays Output and sends input to Shell.
    '''

    __events__ = ('on_ready_to_input',)

    def __init__(self, **kwargs):
        super(InteractiveShellInput, self).__init__(**kwargs)
        self.last_line = None

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 13:
            #For enter
            self.last_line = self.text[self._cursor_pos:]
            self.dispatch('on_ready_to_input')

        return super(InteractiveShellInput, self)._keyboard_on_key_down(window,
                                                                        keycode,
                                                                        text,
                                                                        modifiers)
    
    def insert_text(self, substring, from_undo=False):
        if self.cursor_index() < self._cursor_pos:
            return

        return super(InteractiveShellInput, self).insert_text(substring, from_undo)

    def on_ready_to_input(self, *args):
        pass

    def show_output(self, output):
        self.text += output
        Clock.schedule_once(self._set_cursor_val, 0.1)
    
    def _set_cursor_val(self, *args):
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
    
    font_name = StringProperty('data/fonts/DroidSansMono.ttf')
    '''Indicates the font Style used in the console

    :data:`font` is a :class:`~kivy.properties.StringProperty`,
    Default to 'DroidSansMono'
    '''
    
    font_size = NumericProperty(14)
    '''Indicates the size of the font used for the console

    :data:`font_size` is a :class:`~kivy.properties.NumericProperty`,
    Default to '9'
    '''

    def __init__(self, **kwargs):
        super(PythonConsole, self).__init__()
        self.sh = Shell(self)
        self._thread = InteractiveThread(self.sh)

        Clock.schedule_once(self.run_sh, 0)
        self._ready_to_input = False
        self._exit = False

    def ready_to_input(self, *args):
        self._ready_to_input = True

    def run_sh(self, *args):
        self._thread.start()

    def show_output(self, data, dt):
        self.text_input.show_output(data)

    def _show_prompt(self, *args):
        self.text_input.show_output(self.prompt)

    def get_input(self, prompt):
        import time
        self.prompt = prompt
        Clock.schedule_once(self._show_prompt, 0.1)
        while not self._ready_to_input and not self._exit:
            time.sleep(0.05)

        self._ready_to_input = False
        return self.text_input.last_line
    
    def exit(self):
        self._exit = True
        self.sh.exit()

if __name__ == '__main__':
     runTouchApp(PythonConsole())
