from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

class HelpDialog(BoxLayout):
    rst = ObjectProperty(None)
    
    __events__ = ('on_cancel',)
    
    def on_cancel(self, *args):
        pass