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


class RecentItem(BoxLayout):
    path = StringProperty('')
    '''Contains the application path
       :data:`path` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_press', )

    def on_press(self, *args):
        '''Item pressed
        '''


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

    def add_recent(self, list_files):
        '''To add buttons representing Recent Files.
        :param list_files: array of paths
        '''
        for p in list_files:
            recent_item = RecentItem(path=p)
            self.grid.add_widget(recent_item)
            recent_item.bind(on_press=self.btn_release)
            self.grid.height += recent_item.height

        self.grid.height = max(self.grid.height, self.height)

    def btn_release(self, instance):
        '''Event Handler for 'on_release' of an event.
        '''
        self.root._perform_open(instance.path)


class DesignerStartPage(BoxLayout):

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
