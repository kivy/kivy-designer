from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput


class InputDialog(BoxLayout):
    '''InputDialog is a widget with a TextInput, Cancel and Confirm button.
    '''

    message = StringProperty('')
    '''It is the message to be shown
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    user_input = ObjectProperty()
    '''Is the UserTextInput
        :data:`user_input` is a :class:`~designer.input_dialog.UserTextInput`
    '''

    btn_confirm = ObjectProperty()
    '''Is the button to confirm the input
        :data:`btn_confirm` is a :class:`~kivy.uix.button.Button`
    '''

    lbl_error = ObjectProperty()
    '''Is a Label to show errors
        :data:`lbl_error` is a :class:`~kivy.uix.label.Label`
    '''

    __events__ = ('on_confirm', 'on_cancel')

    def __init__(self, message):
        super(InputDialog, self).__init__()
        self.message = message
        self.user_input.bind(text=self.on_text)

    def on_confirm(self, *args):
        pass

    def on_cancel(self, *args):
        pass

    def get_user_input(self):
        '''
        Returns the user input
        '''
        return self.user_input.text

    def on_text(self, *args):
        self.btn_confirm.disabled = len(args[1]) == 0


class UserTextInput(TextInput):
    '''
    TextInput used by InputDialog.
    Used to filter the input and handle events
    '''

    def __init__(self, **kwargs):
        super(UserTextInput, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        '''
        Override the default insert_text to add a filter
        '''
        s = substring if \
            (substring.isalnum() or substring in ['.', '-', '_']) and \
                len(self.text) < 32 \
            else ""

        return super(UserTextInput, self).insert_text(s, from_undo=from_undo)
