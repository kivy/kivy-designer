from kivy.properties import ObjectProperty, StringProperty, OptionProperty
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


class StatusNavBarButton(Button):
    '''StatusNavBarButton is a :class:`~kivy.uix.button` representing
       the Widgets in the Widget hierarchy of currently selected widget.
    '''

    node = ObjectProperty()


class StatusNavBarSeparator(Label):
    '''StatusNavBarSeparator :class:`~kivy.uix.label.Label`
       Used to separate two Widgets by '>'
    '''

    pass


class StatusNavbar(BoxLayout):
    pass


class StatusMessage(BoxLayout):

    message = StringProperty('bbaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaacc' * 10)
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    icon = StringProperty('')
    '''Message icon path
       :data:`icon` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    type = OptionProperty(None, options=['info', 'alert', 'error'])
    '''Shortcut to usual message icons
       :data:`type` is an
       :class:`~kivy.properties.ObjectProperty` and defaults to None
    '''


class StatusInfo(BoxLayout):

    message = StringProperty('')
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''


class StatusBar(BoxLayout):
    '''StatusBar used to display Widget hierarchy of currently selected
       widget and to display messages.
    '''

    app = ObjectProperty()
    '''Reference to current app instance.
       :data:`app` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    navbar = ObjectProperty()
    '''To be used as parent of :class:`~designer.statusbar.StatusNavBarButton`
       and :class:`~designer.statusbar.StatusNavBarSeparator`.
       :data:`navbar` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    status_message = ObjectProperty()
    '''Instance of :class:`~designer.statusbar.StatusMessage`
       :class:`~kivy.properties.ObjectProperty`
    '''

    status_info = ObjectProperty()
    '''Instance of :class:`~designer.statusbar.StatusInfo`
       :class:`~kivy.properties.ObjectProperty`
    '''

    playground = ObjectProperty()
    '''Instance of
       :data:`playground` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self.update_navbar = Clock.create_trigger(self._update_navbar)

    def _update_navbar(self, *largs):
        '''To update navbar with the parents of currently selected Widget.
        '''

        pass

    def _update_content_width(self, *args):
        '''Updates the statusbar's children sizes to save space
        '''
        nav = self.navbar
        nav_c = self.navbar.children
        mes = self.status_message
        if nav_c == 0:
            mes.size_hint_x = 0.9
            nav.size_hint_x = None
            nav.width = 0
        elif mes.message:
            mes.size_hint_x = 0.4
            nav.size_hint_x = 0.5
        elif not mes.message:
            mes.size_hint_x = None
            mes.width = 0
            nav.size_hint_x = 0.9
