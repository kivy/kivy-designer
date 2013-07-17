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

    code_input = ObjectProperty()
    '''Reference to the :class:`~designer.uix.py_code_input.PyCodeInput`.
       :data:`code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''
