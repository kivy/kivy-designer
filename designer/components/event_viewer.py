import re

from designer.components.property_viewer import PropertyLabel, PropertyViewer
from designer.uix.info_bubble import InfoBubble
from designer.utils.utils import get_current_project, get_designer, show_message
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput


class EventHandlerTextInput(TextInput):
    '''EventHandlerTextInput is used to display/change/remove EventHandler
       for an event
    '''

    eventwidget = ObjectProperty(None)
    '''Current selected widget
       :data:`eventwidget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    eventname = StringProperty('')
    '''Name of current event
       :data:`eventname` is a :class:`~kivy.properties.StringProperty`
    '''

    kv_code_input = ObjectProperty()
    '''Reference to KVLangArea
       :data:`kv_code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text_inserted = BooleanProperty(None)
    '''Specifies whether text has been inserted or not
       :data:`text_inserted` is a :class:`~kivy.properties.BooleanProperty`
    '''

    info_message = StringProperty(None)
    '''Message to be displayed by InfoBubble
       :data:`info_message` is a :class:`~kivy.properties.StringProperty`
    '''

    dropdown = ObjectProperty(None)
    '''DropDown which will be displayed to show possible
       functions for that event
       :data:`dropdown` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def on_touch_down(self, touch):
        '''Default handler for 'on_touch_down' event
        '''
        if self.collide_point(*touch.pos):
            self.info_bubble = InfoBubble(message=self.info_message)
            bubble_pos = list(self.to_window(*self.pos))
            bubble_pos[1] += self.height
            self.info_bubble.show(bubble_pos, 1.5)

        return super(EventHandlerTextInput, self).on_touch_down(touch)

    def show_drop_down_for_widget(self, widget):
        '''Show all functions for a widget in a Dropdown.
        '''
        self.dropdown = DropDown()
        list_funcs = dir(widget)
        for func in list_funcs:
            if '__' not in func and hasattr(getattr(widget, func), '__call__'):
                btn = Button(text=func, size_hint=(None, None),
                             size=(100, 30), shorten=True)
                self.dropdown.add_widget(btn)
                btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
                btn.text_size = [btn.size[0] - 4, btn.size[1]]
                btn.valign = 'middle'

        self.dropdown.open(self)
        self.dropdown.pos = (self.x, self.y)
        self.dropdown.bind(on_select=self._dropdown_select)

    def _dropdown_select(self, instance, value):
        '''Event handler for 'on_select' event of self.dropdown
        '''
        self.text += value

    def on_text(self, instance, value):
        '''Default event handler for 'on_text'
        '''
        if not self.kv_code_input:
            return

        d = get_designer()
        playground = d.ui_creator.playground
        self.kv_code_input.set_event_handler(self.eventwidget,
                                             self.eventname,
                                             self.text)
        if self.text and self.text[-1] == '.':
            if self.text == 'self.':
                self.show_drop_down_for_widget(self.eventwidget)
            ## TODO recursively call eventwidget.parent to get the root widget
            elif self.text == 'root.':
                self.show_drop_down_for_widget(playground.root)

            else:
                _id = self.text.replace('.', '')
                root = playground.root
                widget = None

                if _id in root.ids:
                    widget = root.ids[_id]

                if widget:
                    self.show_drop_down_for_widget(widget)

        elif self.dropdown:
            self.dropdown.dismiss()


class NewEventTextInput(TextInput):
    '''NewEventTextInput is TextInput which is used to create a new event
       for a widget. When event is created then on_create_event is emitted
    '''

    __events__ = ('on_create_event',)

    info_message = StringProperty(None)
    '''Message which will be displayed in the InfoBubble
       :data:`info_message` is a :class:`~kivy.properties.StringProperty`
    '''

    def on_create_event(self, *args):
        '''Default event handler for 'on_create_event'
        '''
        pass

    def on_text_validate(self):
        '''Create a new event to a CustomWidget
        '''
        if self.text[:3] == 'on_':
            self.dispatch('on_create_event')

    def on_touch_down(self, touch):
        '''Default handler for 'on_touch_down' event.
        '''
        if self.collide_point(*touch.pos):
            self.info_bubble = InfoBubble(message=self.info_message)
            bubble_pos = list(self.to_window(*self.pos))
            bubble_pos[1] += self.height
            self.info_bubble.show(bubble_pos, 1.5)

        return super(NewEventTextInput, self).on_touch_down(touch)


class EventLabel(PropertyLabel):
    pass


class EventViewer(PropertyViewer):
    '''EventViewer, to display all the events associated with the widget and
       event handler.
    '''

    designer_tabbed_panel = ObjectProperty(None)
    '''Reference to DesignerTabbedPanel
       :data:`designer_tabbed_panel` is a
       :class:`~kivy.properties.ObjectProperty`
    '''

    def on_widget(self, instance, value):
        '''Default handler for change of 'widget' property
        '''
        self.clear()
        if value is not None:
            self.discover(value)

    def clear(self):
        '''To clear :data:`prop_list`.
        '''
        self.prop_list.clear_widgets()

    def discover(self, value):
        '''To discover all properties and add their
           :class:`~designer.components.property_viewer.PropertyLabel` and
           :class:`~designer.components.property_viewer.PropertyBoolean`/
           :class:`~designer.components.property_viewer.PropertyTextInput`
           to :data:`prop_list`.
        '''

        add = self.prop_list.add_widget
        events = value.events()
        for event in events:
            ip = self.build_for(event)
            if not ip:
                continue
            add(EventLabel(text=event))
            add(ip)

        # check if widget has a class to add custom events
        is_custom_widget = False
        app_widgets = get_current_project().app_widgets
        wdg_name = type(self.widget).__name__
        for wdg in app_widgets:
            if wdg == wdg_name:
                widget = app_widgets[wdg]
                # if has a python file
                if widget.py_path:
                    is_custom_widget = True
                break

        if is_custom_widget:
            # Allow adding a new event only if current widget is a custom rule
            add(EventLabel(text='Type and press enter to \n'
                           'create a new event'))
            txt = NewEventTextInput(
                multiline=False,
                info_message='Type and press enter to create a new event')
            txt.bind(on_create_event=self.create_event)
            add(txt)

    def create_event(self, txt):
        '''This function will create a new event given by 'txt' to the widget.
        '''
        # Find the python file of widget
        py_file = None
        app_widgets = get_current_project().app_widgets
        for rule_name in app_widgets:
            if self.widget.__class__.__name__ == rule_name:
                py_file = app_widgets[rule_name].py_path
                break

        # Open it in DesignerTabbedPannel
        rel_path = py_file.replace(get_current_project().path, '')
        if rel_path[0] == '/' or rel_path[0] == '\\':
            rel_path = rel_path[1:]

        self.designer_tabbed_panel.open_file(py_file, rel_path,
                                             switch_to=True)
        self.rel_path = rel_path
        self.txt = txt
        Clock.schedule_once(self._add_event)

    def _add_event(self, *args):
        '''This function will create a new event given by 'txt' to the widget.
        '''
        # Find the class definition
        py_code_input = None
        txt = self.txt
        rel_path = self.rel_path
        for tab_item in self.designer_tabbed_panel.tab_list:
            if not hasattr(tab_item, 'rel_path'):
                continue
            if tab_item.rel_path == rel_path:
                if hasattr(tab_item.content, 'code_input'):
                    py_code_input = tab_item.content.code_input
                    break

        if py_code_input is None:
            show_message('Failed to create a custom event', 5, 'error')
            return
        pos = -1
        for searchiter in re.finditer(r'class\s+%s\(.+\):' %
                                      type(self.widget).__name__,
                                      py_code_input.text):
            pos = searchiter.end()

        if pos != -1:
            col, row = py_code_input.get_cursor_from_index(pos)
            row += 1
            lines = py_code_input.text.splitlines()
            found_events = False
            events_row = row
            for i in range(row, len(lines)):
                if re.match(r'\s+__events__\s*=\s*\(.+\)', lines[i]):
                    found_events = True
                    events_row = i
                    break

                elif re.match('class\s+[\w\d\_]+\(.+\):', lines[i]):
                    break

                elif re.match('def\s+[\w\d\_]+\(.+\):', lines[i]):
                    break

            if found_events:
                events_col = lines[events_row].rfind(')') - 1
                py_code_input.cursor = events_col, events_row
                py_code_input.insert_text(', "%s" ' % txt.text)

                py_code_input.cursor = 0, events_row + 1
                py_code_input.insert_text(
                    '\n    def %s(self, *args):\n        pass\n' % txt.text
                )
            else:
                py_code_input.text = py_code_input.text[:pos] + \
                    '\n\n    __events__=("%s",)\n\n'\
                    '    def %s(self, *args):\n        pass\n' % \
                    (txt.text, txt.text) +\
                    py_code_input.text[pos:]
            show_message('New event created!', 5, 'info')

    def build_for(self, name):
        '''Creates a EventHandlerTextInput for each property given its name
        '''
        text = self.kv_code_input.get_property_value(self.widget, name)
        return EventHandlerTextInput(
            kv_code_input=self.kv_code_input, eventname=name,
            eventwidget=self.widget, multiline=False, text=text,
            info_message="Set event handler for event %s" % (name))
