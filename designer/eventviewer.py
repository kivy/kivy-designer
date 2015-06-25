from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from designer.uix.info_bubble import InfoBubble
from designer.propertyviewer import PropertyViewer, PropertyLabel

import re


class EventHandlerTextInput(TextInput):
    '''EventHandlerTextInput is used to display/change/remove EventHandler
       for an event
    '''

    eventwidget = ObjectProperty(None)
    '''Current selected widget
       :data:`eventwidget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    eventname = StringProperty(None)
    '''Name of current event
       :data:`eventname` is a :class:`~kivy.properties.ObjectProperty`
    '''

    kv_code_input = ObjectProperty()
    '''Reference to KVLangArea
       :data:`kv_code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text_inserted = BooleanProperty(None)
    '''Specifies whether text has been inserted or not
       :data:`text_inserted` is a :class:`~kivy.properties.ObjectProperty`
    '''

    project_loader = ObjectProperty(None)
    '''Reference to ProjectLoader
       :data:`project_loader` is a :class:`~kivy.properties.ObjectProperty`
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

        self.kv_code_input.set_event_handler(self.eventwidget,
                                             self.eventname,
                                             self.text)
        if self.text and self.text[-1] == '.':
            if self.text == 'self.':
                self.show_drop_down_for_widget(self.eventwidget)

            elif self.text == 'root.':
                self.show_drop_down_for_widget(
                    self.project_loader.root_rule.widget)

            else:
                _id = self.text.replace('.', '')
                root = self.project_loader.root_rule.widget
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

    project_loader = ObjectProperty(None)
    '''Reference to ProjectLoader
       :data:`project_loader` is a :class:`~kivy.properties.ObjectProperty`
    '''

    designer_tabbed_panel = ObjectProperty(None)
    '''Reference to DesignerTabbedPanel
       :data:`designer_tabbed_panel` is a
       :class:`~kivy.properties.ObjectProperty`
    '''

    statusbar = ObjectProperty(None)
    '''Reference to Statusbar
       :data:`statusbar` is a :class:`~kivy.properties.ObjectProperty`
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
           :class:`~designer.propertyviewer.PropertyLabel` and
           :class:`~designer.propertyviewer.PropertyBoolean`/
           :class:`~designer.propertyviewer.PropertyTextInput`
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

        if self.project_loader.is_widget_custom(self.widget):
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
        for rule in self.project_loader.class_rules:
            if self.widget.__class__.__name__ == rule.name:
                py_file = rule.file
                break

        # Open it in DesignerTabbedPannel
        rel_path = py_file.replace(self.project_loader.proj_dir, '')
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
        for code_input in self.designer_tabbed_panel.list_py_code_inputs:
            if code_input.rel_file_path == rel_path:
                py_code_input = code_input
                break

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
            self.statusbar.show_message('New Event Created you must save '
                                        'project for changes to take effect')

    def build_for(self, name):
        '''To create :class:`~designer.propertyviewer.PropertyBoolean`/
           :class:`~designer.propertyviewer.PropertyTextInput`
           for Property 'name'
        '''
        text = self.kv_code_input.get_property_value(self.widget, name)
        return EventHandlerTextInput(
            kv_code_input=self.kv_code_input, eventname=name,
            eventwidget=self.widget, multiline=False, text=text,
            project_loader=self.project_loader,
            info_message="Set event handler for event %s" % (name))
