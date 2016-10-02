from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout


class CodeInputFind(BoxLayout):
    '''Widget responsible for searches in the Python Code Input
    '''

    query = StringProperty('')
    '''Search query
    :data:`query` is a :class:`~kivy.properties.StringProperty`
    '''

    txt_query = ObjectProperty(None)
    '''Search query TextInput
    :data:`txt_query` is a :class:`~kivy.properties.ObjectProperty`
    '''

    use_regex = BooleanProperty(False)
    '''Filter search with regex
        :data:`use_regex` is a :class:`~kivy.properties.BooleanProperty`
    '''

    case_sensitive = BooleanProperty(False)
    '''Filter search with case sensitive text
        :data:`case_sensitive` is a :class:`~kivy.properties.BooleanProperty`
    '''

    __events__ = ('on_close', 'on_next', 'on_prev', )

    def on_touch_down(self, touch):
        '''Enable touche
        '''
        if self.collide_point(*touch.pos):
            super(CodeInputFind, self).on_touch_down(touch)
            return True

    def find_next(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def find_prev(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def on_close(self, *args):
        pass

    def on_next(self, *args):
        pass

    def on_prev(self, *args):
        pass
