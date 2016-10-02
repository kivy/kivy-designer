from kivy.uix.floatlayout import FloatLayout


class AboutDialog(FloatLayout):
    '''AboutDialog, to display about information.
       It emits 'on_cancel' event when 'Cancel' button is released.
    '''

    __events__ = ('on_close',)

    def on_close(self, *args):
        '''Default handler for 'on_close' event
        '''
        pass
