from kivy.uix.codeinput import CodeInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from designer.uix.kivy_console import KivyConsole

class ConsoleDialog(BoxLayout):
    '''It displays the dialog containing tab_pannel with two tabitems
       which has error_console and kivy_console.
    '''
    tab_pannel = ObjectProperty(None)
    '''Instance of :class:`~designer.designer_content.DesignerTabbedPanel`
    '''

    error_console = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.codeinput.CodeInput` used for displaying
       exceptions.
    '''

    kivy_console = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.kivy_console.KivyConsole`.
    '''