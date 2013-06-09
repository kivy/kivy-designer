from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from designer.common import widgets
from kivy.uix.accordion import Accordion, AccordionItem

class ToolboxCategory(AccordionItem):
    gridlayout = BoxLayout(orientation = 'vertical')

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


class Toolbox(BoxLayout):

    accordion = ObjectProperty()
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super(Toolbox, self).__init__(**kwargs)
        Clock.schedule_once(self.discover_widgets, 0)

    def discover_widgets(self, *largs):
        # for now, don't do auto detection of widgets.
        # just do manual discovery, and tagging.

        categories = list(set([x[1] for x in widgets]))
        for category in categories:
            toolbox_category = ToolboxCategory(title=category)
            self.accordion.add_widget(toolbox_category)

            for widget in widgets:
                if widget[1] != category:
                    continue
                toolbox_category.gridlayout.add_widget(
                    ToolboxButton(text=widget[0]))

        self.accordion.children[-1].collapse = False
