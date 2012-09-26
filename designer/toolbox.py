from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from designer.common import widgets


class ToolboxCategory(Label):
    pass


class ToolboxButton(Button):

    def __init__(self, **kwargs):
        self.register_event_type('on_press_and_touch')
        super(ToolboxButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_press_and_touch', touch)
        return super(ToolboxButton, self).on_touch_down(touch)

    def on_press_and_touch(self, touch):
        pass


class Toolbox(FloatLayout):

    widgets_list = ObjectProperty()
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super(Toolbox, self).__init__(**kwargs)
        Clock.schedule_once(self.discover_widgets, 0)

    def discover_widgets(self, *largs):
        # for now, don't do auto detection of widgets.
        # just do manual discovery, and tagging.
        categories = list(set([x[1] for x in widgets]))
        for category in categories:
            self.widgets_list.add_widget(ToolboxCategory(text=category))
            for widget in widgets:
                if widget[1] != category:
                    continue
                self.widgets_list.add_widget(ToolboxButton(text=widget[0]))

