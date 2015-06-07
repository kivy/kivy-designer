from kivy.uix.codeinput import CodeInput
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.scrollview import ScrollView

from designer.uix.designer_code_input import DesignerCodeInput


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
    '''Reference to the :class:`~designer.uix.py_code_input.PyCodeInput`.
       :data:`code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    line_number = ObjectProperty(None)
    '''Text Input to display line numbers
       :data:`line_number` is a :class:`~kivy.properties.ObjectProperty`
    '''

    show_line_number = BooleanProperty(True)
    '''Display line number on left
       :data:`show_line_number` is a :class:`~kivy.properties.BooleanProperty`
       and defaults to True
    '''

    def __init__(self, **kwargs):
        super(PyScrollView, self).__init__(**kwargs)
        self._max_num_of_lines = 0
        if not self.show_line_number:
            self.line_number.parent.remove_widget(self.line_number)
        else:
            self.code_input.bind(_lines=self.on_lines_changed)

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
