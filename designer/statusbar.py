from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanelContent, TabbedPanelHeader, TabbedPanel

from kivy.uix.sandbox import SandboxContent

class StatusNavBarButton(Button):
    '''StatusNavBarButton is a :class:`~kivy.uix.button` representing 
       the Widgets in the Widget heirarchy of currently selected widget.
    '''

    node = ObjectProperty()

class StatusNavBarSeparator(Label):
    '''StatusNavBarSeparator :class:`~kivy.uix.label.Label`
       Used to separate two Widgets by '>'
    '''

    pass

class StatusBar(BoxLayout):
    '''StatusBar used to display Widget heirarchy of currently selected
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

    gridlayout = ObjectProperty()
    '''Parent of :data:`navbar`.
       :data:`gridlayout` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    playground = ObjectProperty()
    '''Instance of 
       :data:`playground` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    def show_message(self, message):
        '''To show a message in StatusBar
        '''

        self.app.widget_focused = None
        if self.gridlayout.children or not \
            isinstance(self.gridlayout.children[0], Label):
            #Create navbar again, as doing clear_widgets will make its reference
            #count to 0 and it will be destroyed
            self.navbar = GridLayout(rows=1)
        
        self.gridlayout.clear_widgets()
        self.gridlayout.add_widget(Label(text=message))
        self.gridlayout.children[0].text = message

    def on_app(self, instance, app):
        app.bind(widget_focused=self.update_navbar)    

    def update_navbar(self, *largs):
        '''To update navbar with the parents of currently selected Widget.
        '''

        if self.gridlayout.children and \
            isinstance(self.gridlayout.children[0], Label):
            self.gridlayout.clear_widgets()
            self.gridlayout.add_widget(self.navbar)

        self.navbar.clear_widgets()
        wid = self.app.widget_focused
        if not wid:
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

