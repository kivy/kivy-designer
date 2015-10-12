from kivy.properties import ObjectProperty, StringProperty, OptionProperty
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelContent, TabbedPanelHeader, \
    TabbedPanel


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

    message = StringProperty('')
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    icon = StringProperty('')
    '''Message icon path
       :data:`icon` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    type = OptionProperty(None, options=['info', 'error', 'loading'],
                          allownone=True)
    '''Shortcut to usual message icons
       :data:`type` is an
       :class:`~kivy.properties.ObjectProperty` and defaults to None
    '''

    def show_message(self, message, duration=5, type=None):
        self.message = message
        self.type = type

        if duration > 0:
            Clock.schedule_once(self.clear_message, duration)

    def clear_message(self, *args):
        self.type = None
        self.message = ''

    def on_type(self, *args):
        icon = ''
        type = self.type
        if type == 'info':
            icon = 'icons/info.png'
        elif type == 'error':
            icon = 'icons/error.png'
        elif type == 'loading':
            icon = 'icons/loading.gif'
        self.icon = icon


class StatusInfo(BoxLayout):

    message = StringProperty('')
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    info = StringProperty('')
    '''Info visible on the status bar
       :data:`info` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    branch = StringProperty('')
    '''Branch name visible on the status bar
       :data:`branch` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    def update_info(self, info, branch_name=None):
        template = info
        if branch_name is not None:
            self.branch = branch_name

        if self.branch:
            template += ' | ' + self.branch

        self.message = template


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

    __events__ = ('on_message_press', 'on_info_press', )

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self.update_navbar = Clock.create_trigger(self._update_navbar)
        self.update_nav_size = Clock.create_trigger(self._update_content_width)

    def _update_navbar(self, *args):
        '''To update navbar with the parents of currently selected Widget.
        '''
        self.navbar.clear_widgets()
        wid = self.app.widget_focused
        if not wid:
            self.update_nav_size()
            return

        # get parent list, until app.root.playground.root
        children = []
        while wid:
            if wid == self.playground.sandbox or\
                    wid == self.playground.sandbox.children[0]:
                break

            if isinstance(wid, TabbedPanelContent):
                _wid = wid
                wid = wid.parent.current_tab
                children.append(StatusNavBarButton(node=wid))
                wid = _wid.parent

            elif isinstance(wid, TabbedPanelHeader):
                children.append(StatusNavBarButton(node=wid))
                _wid = wid
                while _wid and not isinstance(_wid, TabbedPanel):
                    _wid = _wid.parent
                wid = _wid

            children.append(StatusNavBarButton(node=wid))
            wid = wid.parent

        count = len(children)
        for index, child in enumerate(reversed(children)):
            self.navbar.add_widget(child)
            if index < count - 1:
                self.navbar.add_widget(StatusNavBarSeparator())
            else:
                child.state = 'down'

    def on_app(self, instance, app, *args):
        app.bind(widget_focused=self.update_navbar)

    def _update_content_width(self, *args):
        '''Updates the statusbar's children sizes to save space
        '''
        nav = self.navbar.parent
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

    def show_message(self, message, duration=5, type=None, *args):
        '''Shows a message. Use type to change the icon and the duration
        in seconds. Set duration = -1 to undefined time
        '''
        self.status_message.show_message(message, duration, type)

    def update_info(self, info, branch_name=None):
        '''Updates the info message
        '''
        self.status_info.update_info(info, branch_name)

    def on_message_press(self, *args):
        '''Event handler to message widget touch down
        '''
        pass

    def on_info_press(self, *args):
        '''Event handler to info widget touch down
        '''
        pass
