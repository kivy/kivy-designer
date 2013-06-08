from kivy.uix.actionbar import ActionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.properties import ObjectProperty, StringProperty
from functools import partial

class ActionCheckButton(ActionItem, BoxLayout):
    checkbox = ObjectProperty(None)
    text = StringProperty('Check Button')

    __events__ = ('on_active',)

    def __init__(self, **kwargs):
        super(ActionCheckButton, self).__init__(**kwargs)
        self._label = Label(text=self.text)
        self.checkbox = CheckBox()
        self.checkbox.size_hint_x = None
        self.checkbox.x = self.x + 2
        self.checkbox.width = '20sp'
        BoxLayout.add_widget(self, self.checkbox)
        BoxLayout.add_widget(self, self._label)
        self.checkbox.bind(on_active=partial(self.dispatch, 'on_active'))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.checkbox.active = not self.checkbox.active

    def on_active(self, *args):
        pass

    def on_text(self, instance, value):
        self._label.text = value
