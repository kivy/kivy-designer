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
    '''

class PyScrollView(ScrollView):
    '''PyScrollView used as a ScrollView for adding PyCodeInput.
    '''

    code_input = ObjectProperty()
    '''Reference to the PyCodeInput
    '''