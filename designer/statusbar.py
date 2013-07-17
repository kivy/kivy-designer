from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

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
        self.clear_widgets()
        label = Label(text=message)
        self.add_widget(label)

    def on_app(self, instance, app):
        app.bind(widget_focused=self.update_navbar)

    def update_navbar(self, *largs):
        '''To update navbar with the parents of currently selected Widget.
        '''

        self.clear_widgets()
        self.add_widget(self.gridlayout)
        self.navbar.clear_widgets()

        wid = self.app.widget_focused
        if not wid:
            return

        # get parent list, until app.root.playground.root
        children = []
        while True:
            if wid == self.playground.sandbox:
                break
            children.append(StatusNavBarButton(node=wid))
            wid = wid.parent

        count = len(children)
        for index, child in enumerate(reversed(children)):
            self.navbar.add_widget(child)
            if index < count - 1:
                self.navbar.add_widget(StatusNavBarSeparator())
            else:
                child.state = 'down'

