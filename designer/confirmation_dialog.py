from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty


class ConfirmationDialog(BoxLayout):
    '''ConfirmationDialog shows a confirmation message with two buttons
       "Yes" and "No". It may be used for confirming user about an operation.
       It emits 'on_ok' when "Yes" is pressed and 'on_cancel' when "No" is
       pressed.
    '''

    message = StringProperty('')
    '''It is the message to be shown
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_ok', 'on_cancel')

    def __init__(self, message):
        super(ConfirmationDialog, self).__init__()
        self.message = message

    def on_ok(self, *args):
        pass

    def on_cancel(self, *args):
        pass
