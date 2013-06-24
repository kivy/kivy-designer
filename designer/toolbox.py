from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from designer.common import widgets
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.metrics import pt

class ToolboxCategory(AccordionItem):
    gridlayout = ObjectProperty(None)


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
        self.custom_category = None

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
    
    def cleanup(self):
        if self.custom_category:
            self.custom_category.gridlayout.clear_widgets()

    def add_custom(self):
        if not self.custom_category:
            self.custom_category = ToolboxCategory(title='custom')
            
            #FIXME: ToolboxCategory keeps on adding more scrollview,
            #if they are initialized again, unable to find the cause of problem
            #I just decided to delete those scrollview whose childs are not 
            #self.gridlayout.
            _scrollview_parent = self.custom_category.gridlayout.parent.parent
            for child in _scrollview_parent.children[:]:
                if child.children[0] != self.custom_category.gridlayout:
                    _scrollview_parent.remove_widget(child)
                
            self.accordion.add_widget(self.custom_category)
        else:
            self.custom_category.gridlayout.clear_widgets()

        for widget in widgets:
            if widget[1] == 'custom':
                self.custom_category.gridlayout.add_widget(
                    ToolboxButton(text=widget[0]))
        
        #Setting appropriate height to gridlayout to enable scrolling
        self.custom_category.gridlayout.size_hint_y = None
        self.custom_category.gridlayout.height = \
            (len(self.custom_category.gridlayout.children)+5)*pt(22)
            