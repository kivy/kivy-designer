import jedi

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.scrollview import ScrollView
from designer.uix.completion_bubble import CompletionBubble

from designer.uix.designer_code_input import DesignerCodeInput

MarkupLabel = None


class PyCodeInput(DesignerCodeInput):
    '''PyCodeInput used as the CodeInput for editing Python Files.
       It's rel_file_path property, gives the file path of the file it is
       currently displaying relative to Project Directory
    '''

    rel_file_path = StringProperty('')
    '''Path of file relative to the Project Directory.
       To get full path of file, use os.path.join
       :data:`rel_file_path` is a :class:`~kivy.properties.StringProperty`
    '''


class PyScrollView(ScrollView):
    '''PyScrollView used as a :class:`~kivy.scrollview.ScrollView`
       for adding :class:`~designer.uix.py_code_input.PyCodeInput`.
    '''

    code_input = ObjectProperty(None)
    '''(internal) Reference to the
        :class:`~designer.uix.py_code_input.PyCodeInput`.
       :data:`code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    line_number = ObjectProperty(None)
    '''(internal) Text Input to display line numbers
       :data:`line_number` is a :class:`~kivy.properties.ObjectProperty`
    '''

    bubble = ObjectProperty(None)
    '''(internal) Bubble to display completions suggestion
       :data:`line_number` is a :class:`~kivy.properties.ObjectProperty`
    '''

    is_bubble_visible = BooleanProperty(False)
    '''(internal) If bubble is visible in the screen
       :data:`line_number` is a :class:`~kivy.properties.ObjectProperty`
    '''

    show_line_number = BooleanProperty(True)
    '''Display line number on left
       :data:`show_line_number` is a :class:`~kivy.properties.BooleanProperty`
       and defaults to True
    '''

    use_autocompletion = BooleanProperty(True)
    '''Use autocompletion
       :data:`use_autocompletion` is a :class:`~kivy.properties.BooleanProperty`
       and defaults to True
    '''

    def __init__(self, **kwargs):
        super(PyScrollView, self).__init__(**kwargs)
        self._max_num_of_lines = 0
        self.bubble = CompletionBubble()
        self.bubble.bind(on_cancel=self.cancel_completion)
        self.bubble.bind(on_complete=self.on_complete)
        self.root = App.get_running_app().root

        if self.use_autocompletion:
            self.code_input.bind(focus=self.on_code_input_focus)

        if not self.show_line_number:
            self.line_number.parent.remove_widget(self.line_number)
        else:
            self.code_input.bind(_lines=self.on_lines_changed)

    def on_code_input_focus(self, *args):
        '''Focus on CodeInput, to enable/disable keyboard listener
        '''
        if args[1]:
            Window.bind(on_keyboard=self.on_keyboard)
        else:
            Window.unbind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 32 and modifier == ['ctrl']:
            code = self.code_input
            src = code.text
            line = code.cursor_row + 1
            col = code.cursor_col
            script = jedi.Script(src, line, col)
            completions = script.completions()
            self.show_completion(completions)

    def on_complete(self, instance, completion):
        '''Add the completion to the current cursor position
        '''
        self.code_input.insert_text(completion)
        self.cancel_completion()

    def show_completion(self, completions):
        '''Display the bubble with the completions
        '''
        self.bubble.show_completions(completions, force_scroll=True)
        self.bubble.reposition(
            self.code_input.to_window(*self.code_input.cursor_pos),
            self.code_input.line_height + self.code_input.line_spacing
        )
        self.root.add_widget(self.bubble)
        self.is_bubble_visible = True

    def cancel_completion(self, *args):
        '''Event handler to cancel the completion
        '''
        if self.bubble.parent is not None:
            self.bubble.show_completions([])
            self.bubble.parent.remove_widget(self.bubble)
            self.is_bubble_visible = False

    def on_lines_changed(self, *args):
        '''Event handler that listen the line modifications to update
        line_number
        '''
        n = len(self.code_input._lines)
        if n > self._max_num_of_lines:
            self.update_line_number(self._max_num_of_lines, n)

    def update_line_number(self, old, new):
        '''Analyze the difference between old and new number of lines
        to update the text input
        '''
        self._max_num_of_lines = new
        self.line_number.text += \
                    '\n'.join([str(i) for i in range(old + 1, new + 1)]) + '\n'
        self.line_number.width = self.line_number._label_cached.get_extents(
            str(self._max_num_of_lines))[0] + (self.line_number.padding[0] * 2)
        # not removing lines, as long as extra lines will not be visible


class PyCodeInputFind(BoxLayout):
    '''Widget responsible for searches in the Python Code Input
    '''

    query = StringProperty('')
    '''Search query
    :data:`query` is a :class:`~kivy.properties.StringProperty`
    '''

    txt_query = ObjectProperty(None)
    '''Search query TextInput
    :data:`txt_query` is a :class:`~kivy.properties.ObjectProperty`
    '''

    use_regex = BooleanProperty(False)
    '''Filter search with regex
        :data:`use_regex` is a :class:`~kivy.properties.BooleanProperty`
    '''

    case_sensitive = BooleanProperty(False)
    '''Filter search with case sensitive text
        :data:`case_sensitive` is a :class:`~kivy.properties.BooleanProperty`
    '''

    __events__ = ('on_close', 'on_next', 'on_prev', )

    def on_touch_down(self, touch):
        '''Enable touche
        '''
        if self.collide_point(*touch.pos):
            super(PyCodeInputFind, self).on_touch_down(touch)
            return True

    def find_next(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def find_prev(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def on_close(self, *args):
        pass

    def on_next(self, *args):
        pass

    def on_prev(self, *args):
        pass
