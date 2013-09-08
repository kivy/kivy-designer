import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import pt

class DesignerLinkLabel(Button):
    link = StringProperty(None)
    
    def on_release(self, *args):
        if self.link:
            webbrowser.open(self.link)

class RecentFilesBox(ScrollView):
    grid = ObjectProperty(None)
    root = ObjectProperty(None)

    def add_recent(self, list_files):
        for i in list_files:
            btn = Button(text=i, size_hint_y=None, height=pt(22))
            self.grid.add_widget(btn)
            btn.bind(size=self._btn_size_changed)
            btn.bind(on_release=self.btn_release)
            btn.valign = 'middle'
            self.grid.height += btn.height

        self.grid.height = max(self.grid.height, self.height)

    def _btn_size_changed(self, instance, value):
        instance.text_size = value
    
    def btn_release(self, instance):
        self.root._perform_open(instance.text)

class DesignerStartPage(GridLayout):
    btn_open = ObjectProperty(None)
    btn_new = ObjectProperty(None)
    recent_files_box = ObjectProperty(None)
    kivy_link = ObjectProperty(None)
    designer_link = ObjectProperty(None)
    
    __events__ = ('on_open_down', 'on_new_down')
    
    def on_open_down(self, *args):
        pass
    
    def on_new_down(self, *args):
        pass