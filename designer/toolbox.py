from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from designer.common import widgets
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.metrics import pt
from kivy.factory import Factory


class ToolboxCategory(AccordionItem):
    '''ToolboxCategory is responsible for grouping and showing
       :class:`~designer.toolbox.ToolboxButton`
       of same class into one category.
    '''

    gridlayout = ObjectProperty(None)
    '''An instance of :class:`~kivy.uix.gridlayout.GridLayout`.
       :data:`gridlayout` is an
       :class:`~kivy.properties.ObjectProperty`
    '''


class ToolboxButton(Button):
    '''ToolboxButton is a subclass of :class:`~kivy.uix.button.Button`,
       to display class of Widgets in
       :class:`~designer.toolbox.ToolboxCategory`.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_press_and_touch')
        super(ToolboxButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        '''Default handler for 'on_touch_down'
        '''
        if self.collide_point(*touch.pos):
            self.dispatch('on_press_and_touch', touch)
        return super(ToolboxButton, self).on_touch_down(touch)

    def on_press_and_touch(self, touch):
        '''Default handler for 'on_press_and_touch' event
        '''
        pass


class Toolbox(BoxLayout):
    '''Toolbox is used to display all the widgets in designer.common.widgets
       in their respective classes.
    '''

    accordion = ObjectProperty()
    '''An instance to :class:`~kivy.uix.accordion.Accordion`,
       used to show Widgets in their groups.
       :data:`accordion` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    app = ObjectProperty()
    '''An instance to the current running app.
       :data:`app` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(Toolbox, self).__init__(**kwargs)
        Clock.schedule_once(self.discover_widgets, 0)
        self.custom_category = None
        self._list = []

    def discover_widgets(self, *largs):
        '''To create and add ToolboxCategory and ToolboxButton for widgets in
           designer.common.widgets
        '''
        # for now, don't do auto detection of widgets.
        # just do manual discovery, and tagging.

        categories = list(set([x[1] for x in widgets]))
        categories.sort()
        for category in categories:
            toolbox_category = ToolboxCategory(title=category)
            self.accordion.add_widget(toolbox_category)

            cat_widgets = []
            for widget in widgets:
                if widget[1] == category:
                    cat_widgets.append(widget)

            cat_widgets.sort()
            for widget in cat_widgets:
                toolbox_category.gridlayout.add_widget(
                    ToolboxButton(text=widget[0]))

        self.accordion.children[-1].collapse = False

    def cleanup(self):
        '''To clean all the children in self.custom_category.
        '''
        if self.custom_category:
            self.accordion.remove_widget(self.custom_category)
            Factory.register('BoxLayout', module='kivy.uix.boxlayout')
            self.custom_category = ToolboxCategory(title='custom')
            self._list.append(self.custom_category)

            # FIXME: ToolboxCategory keeps on adding more scrollview,
            # if they are initialized again, unable to find the cause of problem
            # I just decided to delete those scrollview whose childs are not
            # self.gridlayout.
            _scrollview_parent = self.custom_category.gridlayout.parent.parent
            for child in _scrollview_parent.children[:]:
                if child.children[0] != self.custom_category.gridlayout:
                    _scrollview_parent.remove_widget(child)

    def add_custom(self):
        '''To add/update self.custom_category with new custom classes loaded
           by project.
        '''
        self.custom_category = ToolboxCategory(title='custom')
        self._list.append(self.custom_category)

        self.accordion.add_widget(self.custom_category)

        custom_widgets = []
        for widget in widgets:
            if widget[1] == 'custom':
                custom_widgets.append(widget)

        custom_widgets.sort()
        for widget in custom_widgets:
            self.custom_category.gridlayout.add_widget(
                ToolboxButton(text=widget[0]))

        # Setting appropriate height to gridlayout to enable scrolling
        self.custom_category.gridlayout.size_hint_y = None
        self.custom_category.gridlayout.height = \
            (len(self.custom_category.gridlayout.children) + 5) * pt(22)
