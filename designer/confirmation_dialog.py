from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty

class ConfirmationDialog(BoxLayout):

    message = StringProperty('')
    
    __events__ = ('on_ok', 'on_cancel')
    
    def __init__(self, message):
        super(ConfirmationDialog, self).__init__()
        self.message = message
    
    def on_ok(self, *args):
        pass
    
    def on_cancel(self, *args):
        pass
