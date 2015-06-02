from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout


class HelpDialog(BoxLayout):
    '''HelpDialog, in which help will be displayed from help.rst.
       It emits 'on_cancel' event when 'Cancel' button is released.
    '''

    rst = ObjectProperty(None)
    '''rst is reference to `kivy.uix.rst.RstDocument` to display help from
       help.rst
    '''

    __events__ = ('on_cancel',)

    def on_cancel(self, *args):
        '''Default handler for 'on_cancel' event
        '''
        pass


class AboutDialog(FloatLayout):
    '''AboutDialog, to display about information.
       It emits 'on_cancel' event when 'Cancel' button is released.
    '''

    __events__ = ('on_cancel',)

    def on_cancel(self, *args):
        '''Default handler for 'on_cancel' event
        '''
        pass
