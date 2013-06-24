from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class StatusNavBarButton(Button):
    node = ObjectProperty()

class StatusNavBarSeparator(Label):
    pass

class StatusBar(BoxLayout):
    app = ObjectProperty()
    navbar = ObjectProperty()

    def on_app(self, instance, app):
        app.bind(widget_focused=self.update_navbar)

    def update_navbar(self, *largs):
        self.navbar.clear_widgets()
        wid = self.app.widget_focused
        if not wid:
            return

        # get parent list, until app.root.playground.root
        children = []
        while True:
            if wid == self.app.root.playground.sandbox:
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

