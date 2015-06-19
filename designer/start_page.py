import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import pt
from kivy.clock import Clock


class DesignerLinkLabel(Button):
    '''DesignerLinkLabel displays a http link and opens it in a browser window
       when clicked.
    '''

    link = StringProperty(None)
    '''Contains the http link to be opened.
       :data:`link` is a :class:`~kivy.properties.StringProperty`
    '''

    def on_release(self, *args):
        '''Default event handler for 'on_release' event.
        '''
        if self.link:
            webbrowser.open(self.link)


class RecentFilesBox(ScrollView):
    '''Container consistings of buttons, with their names specifying
       the recent files.
    '''

    grid = ObjectProperty(None)
    '''The grid layout consisting of all buttons.
       This property is an instance of :class:`~kivy.uix.gridlayout`
       :data:`grid` is a :class:`~kivy.properties.ObjectProperty`
    '''

    root = ObjectProperty(None)
    '''Reference to :class:`~designer.app.Designer`
       :data:`root` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(RecentFilesBox, self).__init__(**kwargs)

    def _setup_width(self, *args):
        '''To set appropriate width of RecentFilesBox.
        '''
        max_width = -1
        for child in self.grid.children:
            max_width = max(child.texture_size[0], max_width)

        self.width = max_width + pt(20)

    def add_recent(self, list_files):
        '''To add buttons representing Recent Files.
        '''
        for i in list_files:
            btn = Button(text=i, size_hint_y=None, height=pt(22))
            self.grid.add_widget(btn)
            btn.bind(size=self._btn_size_changed)
            btn.bind(on_release=self.btn_release)
            btn.valign = 'middle'
            self.grid.height += btn.height

        self.grid.height = max(self.grid.height, self.height)
        Clock.schedule_once(self._setup_width, 0.01)

    def _btn_size_changed(self, instance, value):
        '''Event Handler for 'on_size' of buttons added.
        '''
        instance.text_size = value

    def btn_release(self, instance):
        '''Event Handler for 'on_release' of an event.
        '''
        self.root._perform_open(instance.text)


class DesignerStartPage(GridLayout):
    '''This is the start page of the Designer. It will contain two buttons
       'Open Project' and 'New Project', two DesignerLinkLabel
       'Kivy' and 'Kivy Designer Help' and a RecentFilesBox. It emits two
       events 'on_open_down' when 'Open Project' is clicked and
       'on_new_down' when 'New Project' is clicked.
    '''

    btn_open = ObjectProperty(None)
    '''The 'Open Project' Button.
       This property is an instance of :class:`~kivy.uix.button`
       :data:`btn_open` is a :class:`~kivy.properties.ObjectProperty`
    '''

    btn_new = ObjectProperty(None)
    '''The 'New Project' Button.
       This property is an instance of :class:`~kivy.uix.button`
       :data:`btn_new` is a :class:`~kivy.properties.ObjectProperty`
    '''

    recent_files_box = ObjectProperty(None)
    '''This property is an instance
        of :class:`~designer.start_page.RecentFilesBox`
       :data:`recent_files_box` is a :class:`~kivy.properties.ObjectProperty`
    '''

    kivy_link = ObjectProperty(None)
    '''The 'Kivy' DesignerLinkLabel.
       :data:`kivy_link` is a :class:`~kivy.properties.ObjectProperty`
    '''

    designer_link = ObjectProperty(None)
    '''The 'Kivy Designer Help' DesignerLinkLabel.
       :data:`designer_link` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_open_down', 'on_new_down', 'on_help')

    def on_open_down(self, *args):
        '''Default Event Handler for 'on_open_down'
        '''
        pass

    def on_new_down(self, *args):
        '''Default Event Handler for 'on_new_down'
        '''
        pass

    def on_help(self, *args):
        '''Default Event Handler for 'on_help'
        '''
        pass
